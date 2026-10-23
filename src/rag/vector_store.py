"""ChromaDB persistente com invalidação e reconstrução transacional do índice."""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import uuid
from pathlib import Path
from langchain_chroma import Chroma
from .settings import (
    CHROMA_PERSIST_DIR, COLLECTION_NAME, EMBEDDING_MODEL, EMBEDDING_HOST,
    KNOWLEDGE_BASE_DIR, ROOT_DIR, CHUNK_SIZE, CHUNK_OVERLAP,
)
from .loader import load_knowledge_base
from .chunking import split_documents
from .embeddings import create_embeddings
from .manual_gate import require_official_manual

META_PATH = ROOT_DIR / "storage" / "chroma_index_metadata.json"


def _corpus_hash() -> str:
    digest = hashlib.sha256()
    for path in sorted(KNOWLEDGE_BASE_DIR.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".pdf", ".md", ".txt", ".csv"} and path.name.lower() != "readme.md":
            digest.update(path.name.encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _metadata() -> dict:
    return {
        "corpus_sha256": _corpus_hash(),
        "embedding_model": EMBEDDING_MODEL,
        "embedding_host": EMBEDDING_HOST,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "collection": COLLECTION_NAME,
    }


def _close_store_client(store) -> None:
    """Tenta parar o cliente persistente antes de mover diretórios no Windows."""
    client = getattr(store, "_client", None)
    system = getattr(client, "_system", None)
    stop = getattr(system, "stop", None)
    if callable(stop):
        stop()


def _collection_count(store) -> int:
    try:
        return int(store._collection.count())
    except Exception as exc:
        raise RuntimeError("Não foi possível validar a quantidade de chunks no ChromaDB.") from exc


def build_or_load_vector_store(force_rebuild: bool = False) -> Chroma:
    """Abre a coleção persistente; reconstrói em staging e só troca após validação.

    O manual oficial GoodWe é obrigatório. Uma falha de embedding ou na construção
    não apaga o índice antigo: ele só é movido depois que o staging contém chunks.
    """
    require_official_manual(KNOWLEDGE_BASE_DIR)
    current = _metadata()
    saved = None
    if META_PATH.exists():
        try:
            saved = json.loads(META_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            saved = None

    store_exists = CHROMA_PERSIST_DIR.exists() and any(CHROMA_PERSIST_DIR.iterdir())
    if not force_rebuild and store_exists and saved == current:
        try:
            existing = Chroma(
                collection_name=COLLECTION_NAME,
                persist_directory=str(CHROMA_PERSIST_DIR),
                embedding_function=create_embeddings(),
            )
            if _collection_count(existing) > 0:
                return existing
            _close_store_client(existing)
        except Exception:
            # Índice inconsistente: constrói staging sem destruir a versão antiga.
            pass

    CHROMA_PERSIST_DIR.parent.mkdir(parents=True, exist_ok=True)
    META_PATH.parent.mkdir(parents=True, exist_ok=True)
    unique = uuid.uuid4().hex[:10]
    staging = CHROMA_PERSIST_DIR.parent / f".{CHROMA_PERSIST_DIR.name}.staging-{unique}"
    backup = CHROMA_PERSIST_DIR.parent / f".{CHROMA_PERSIST_DIR.name}.backup-{unique}"
    meta_temp = META_PATH.with_name(f".{META_PATH.name}.tmp-{unique}")
    staged_store = None
    final_store = None
    old_index_moved = False
    new_index_installed = False

    try:
        documents = load_knowledge_base()
        chunks = split_documents(documents)
        if not chunks:
            raise RuntimeError("O splitter não gerou chunks; confira a base de conhecimento.")

        staged_store = Chroma.from_documents(
            documents=chunks,
            embedding=create_embeddings(),
            collection_name=COLLECTION_NAME,
            persist_directory=str(staging),
        )
        count = _collection_count(staged_store)
        if count < 1:
            raise RuntimeError("O ChromaDB de staging ficou sem chunks; índice anterior preservado.")
        _close_store_client(staged_store)
        staged_store = None

        # Mesma unidade/volume para possibilitar renomeação local. Se o Windows
        # bloquear por outro processo, a exceção ocorre antes de apagar o índice antigo.
        if CHROMA_PERSIST_DIR.exists():
            CHROMA_PERSIST_DIR.rename(backup)
            old_index_moved = True
        staging.rename(CHROMA_PERSIST_DIR)
        new_index_installed = True

        # Confere se o índice instalado pode ser aberto e lido antes de publicar metadata.
        final_store = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=str(CHROMA_PERSIST_DIR),
            embedding_function=create_embeddings(),
        )
        if _collection_count(final_store) != count:
            raise RuntimeError("A contagem do índice instalado diverge do staging; rollback iniciado.")

        meta_temp.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(meta_temp, META_PATH)
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
        return final_store

    except Exception:
        if final_store is not None:
            try:
                _close_store_client(final_store)
            except Exception:
                pass
        if new_index_installed and CHROMA_PERSIST_DIR.exists():
            # Retira o índice novo para restaurar o anterior se havia backup.
            try:
                if staging.exists():
                    shutil.rmtree(staging, ignore_errors=True)
                CHROMA_PERSIST_DIR.rename(staging)
            except Exception:
                # Mantém os diretórios para recuperação manual, nunca os apaga à força.
                pass
        if old_index_moved and backup.exists() and not CHROMA_PERSIST_DIR.exists():
            try:
                backup.rename(CHROMA_PERSIST_DIR)
            except Exception:
                pass
        if staged_store is not None:
            try:
                _close_store_client(staged_store)
            except Exception:
                pass
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        try:
            meta_temp.unlink(missing_ok=True)
        except OSError:
            pass
        raise

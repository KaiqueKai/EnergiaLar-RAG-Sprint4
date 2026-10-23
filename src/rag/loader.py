"""Carregamento da base: PyMuPDFLoader para PDFs, TextLoader e CSVLoader para arquivos textuais."""
from __future__ import annotations
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, CSVLoader
from langchain_core.documents import Document
from .settings import KNOWLEDGE_BASE_DIR, ROOT_DIR
from .security import sanitize_untrusted_text

SOURCE_URLS = {
    "00_manual_oficial_goodwe_hca_g2_en.pdf": "https://br.goodwe.com/Api/downloadFile?id=2496&mid=60&type=2",
    "00b_compatibilidade_goodwe_ev_hca_g2_en.pdf": "https://br.goodwe.com/Api/downloadFile?id=4535&mid=60&type=2",
    "01_folha_dados_hca_g2.md": "https://br.goodwe.com/download-hca-g2-series",
    "02_faq_energialar_recarga.md": "https://github.com/KaiqueKai/EnergiaLar",
    "03_condominio_protocolo_orientativo.md": "",
    # Os valores do CSV são exemplos simulados, não extraídos da página da distribuidora.
    "04_tarifas_referencia.csv": "",
    "05_perguntas_de_validacao.md": "https://github.com/KaiqueKai/EnergiaLar",
    # O resumo 06 inclui duas leis; os links primários estão dentro do próprio documento.
    "06_referencias_condominiais_sp.md": "",
    "07_tarifas_oficiais_enel_sp_2026.md": "https://www.enel.com.br/pt-saopaulo/Para_Voce/tarifa-energia-eletrica.html",
    "07_tarifas_oficiais_enel_sp_2026.csv": "https://www.enel.com.br/pt-saopaulo/Para_Voce/tarifa-energia-eletrica.html",
}
SUPPORTED = {".pdf", ".md", ".txt", ".csv"}


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT_DIR.resolve())).replace("\\", "/")
    except ValueError:
        return path.name


def load_knowledge_base() -> list[Document]:
    """Lê os arquivos autorizados da KB e remove linhas de prompt injection detectáveis."""
    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(f"Pasta de conhecimento não encontrada: {KNOWLEDGE_BASE_DIR}")
    documents: list[Document] = []
    for path in sorted(KNOWLEDGE_BASE_DIR.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED or path.name.lower() == "readme.md":
            continue
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            loaded = PyMuPDFLoader(str(path)).load()
        elif suffix == ".csv":
            loaded = CSVLoader(str(path), encoding="utf-8").load()
        else:
            loaded = TextLoader(str(path), encoding="utf-8").load()
        for raw in loaded:
            safe_text = sanitize_untrusted_text(raw.page_content)
            if not safe_text:
                continue
            page_value = raw.metadata.get("page")
            metadata = {
                "source": _relative(path),
                "source_name": path.name,
                "source_url": SOURCE_URLS.get(path.name, ""),
                "page": int(page_value) if isinstance(page_value, int) else -1,
            }
            documents.append(Document(page_content=safe_text, metadata=metadata))
    if not documents:
        raise RuntimeError("Nenhum documento compatível foi encontrado em data/knowledge_base.")
    return documents

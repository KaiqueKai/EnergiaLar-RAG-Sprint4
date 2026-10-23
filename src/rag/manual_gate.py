"""Gate de completude: índice final só é criado com o manual oficial HCA G2."""
from __future__ import annotations
from pathlib import Path
import fitz

OFFICIAL_MANUAL_NAME = "00_manual_oficial_goodwe_hca_g2_en.pdf"
MINIMUM_PDF_BYTES = 10_000


def require_official_manual(knowledge_base_dir: Path) -> Path:
    """Valida presença, tamanho, cabeçalho e estrutura PDF do manual oficial."""
    path = Path(knowledge_base_dir) / OFFICIAL_MANUAL_NAME
    if not path.is_file():
        raise FileNotFoundError(
            "O manual oficial GoodWe HCA G2 está ausente. Baixe-o com "
            "scripts/baixar_manual_oficial.ps1 ou salve-o em "
            f"data/knowledge_base/{OFFICIAL_MANUAL_NAME}. O índice final não será criado sem esse documento."
        )
    if path.stat().st_size < MINIMUM_PDF_BYTES:
        raise ValueError(f"O manual oficial parece incompleto (menos de {MINIMUM_PDF_BYTES} bytes): {path}")
    with path.open("rb") as stream:
        header = stream.read(5)
    if header != b"%PDF-":
        raise ValueError(f"O arquivo do manual não contém cabeçalho PDF válido: {path}")
    try:
        with fitz.open(path) as document:
            if document.page_count < 1:
                raise ValueError("O PDF do manual não contém páginas.")
            # Documentos oficiais precisam fornecer texto indexável, evitando que
            # uma imagem vazia ou um HTML salvo como PDF libere o gate por engano.
            text = "\n".join(page.get_text("text") for page in document[: min(3, document.page_count)]).strip()
            if len(text) < 80:
                raise ValueError("O PDF do manual não contém texto indexável suficiente nas primeiras páginas.")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Não foi possível abrir/validar o PDF do manual: {type(exc).__name__}") from exc
    return path

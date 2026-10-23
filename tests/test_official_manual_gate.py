from pathlib import Path
import fitz
import pytest

from src.rag.manual_gate import OFFICIAL_MANUAL_NAME, require_official_manual


def _valid_pdf(path: Path, pages: int = 3) -> None:
    document = fitz.open()
    body = ("GoodWe HCA G2 official user manual. Safety, operation, configuration, "
            "charging mode and installation must follow the current model-specific "
            "instructions and local electrical regulations. ") * 20
    for _ in range(pages):
        page = document.new_page()
        page.insert_textbox(fitz.Rect(48, 48, 540, 760), body, fontsize=10)
    document.save(path, garbage=4, deflate=True)
    document.close()
    # Add a harmless comment after the PDF EOF marker to test the configured size gate;
    # MuPDF still validates the actual document structure and text.
    if path.stat().st_size < 10_000:
        with path.open("ab") as stream:
            stream.write(b"\n% supplemental padding for automated gate test\n" * 300)


def test_manual_gate_rejects_missing_official_pdf(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="manual oficial"):
        require_official_manual(tmp_path)


def test_manual_gate_rejects_non_pdf_file(tmp_path: Path):
    path = tmp_path / OFFICIAL_MANUAL_NAME
    path.write_bytes(b"NOTPDF" + b"x" * 10_100)
    with pytest.raises(ValueError, match="cabeçalho PDF"):
        require_official_manual(tmp_path)


def test_manual_gate_rejects_pdf_header_without_valid_pdf_structure(tmp_path: Path):
    path = tmp_path / OFFICIAL_MANUAL_NAME
    path.write_bytes(b"%PDF-1.7\n" + b"x" * 10_100)
    with pytest.raises(ValueError, match="abrir/validar|texto indexável|páginas"):
        require_official_manual(tmp_path)


def test_manual_gate_accepts_real_text_pdf_over_minimum_size(tmp_path: Path):
    path = tmp_path / OFFICIAL_MANUAL_NAME
    _valid_pdf(path)
    assert require_official_manual(tmp_path) == path

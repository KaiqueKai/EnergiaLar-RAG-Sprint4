import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_official_enel_tariffs_have_primary_source_vigency_and_correct_b1_values():
    path = ROOT / "data" / "knowledge_base" / "07_tarifas_oficiais_enel_sp_2026.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    conventional = {(row["componente"], row["modalidade"]): row for row in rows if row["classe"] == "B1 residencial" and row["modalidade"] == "Convencional"}
    assert conventional[("TUSD", "Convencional")]["valor_r_mwh"] == "472.42"
    assert conventional[("TE - BVD", "Convencional")]["valor_r_mwh"] == "316.96"
    assert all(row["vigente_desde"] == "2026-07-04" for row in rows)
    assert all("enel.com.br" in row["fonte"] for row in rows)
    assert all("não é custo final" in row["observacao"].lower() for row in rows)

def test_tariff_markdown_distinguishes_components_from_final_bill():
    text = (ROOT / "data" / "knowledge_base" / "07_tarifas_oficiais_enel_sp_2026.md").read_text(encoding="utf-8")
    assert "472,42" in text and "316,96" in text
    assert "não é o valor final da conta" in text.lower() or "não equivale" in text.lower()

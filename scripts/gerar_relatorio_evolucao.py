from __future__ import annotations
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
REPORT_PDF = ROOT / "docs" / "relatorio_evolucao_sprint4.pdf"
RESULTS = ROOT / "evals" / "results"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.HexColor("#17324D"), alignment=TA_LEFT, spaceAfter=10))
styles.add(ParagraphStyle(name="SubTitleCustom", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#4B5D6B"), spaceAfter=6))
styles.add(ParagraphStyle(name="H1Custom", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=14, leading=17, textColor=colors.HexColor("#17324D"), spaceBefore=3, spaceAfter=7))
styles.add(ParagraphStyle(name="H2Custom", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=colors.HexColor("#176B74"), spaceBefore=5, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=11.2, spaceAfter=5))
styles.add(ParagraphStyle(name="SmallCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=7, leading=8.5, spaceAfter=2))
styles.add(ParagraphStyle(name="TableCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.8, leading=8.4, spaceAfter=0))
styles.add(ParagraphStyle(name="TableHeadCustom", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7, leading=8.5, textColor=colors.white, spaceAfter=0))
styles.add(ParagraphStyle(name="CalloutCustom", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.2, leading=10.5, textColor=colors.HexColor("#8A3C16"), backColor=colors.HexColor("#FFF2E7"), borderPadding=6, spaceBefore=4, spaceAfter=7))


def p(text, style="BodyCustom"):
    return Paragraph(escape(str(text)), styles[style])


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D6DEE5"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#687786"))
    canvas.drawString(18 * mm, 9 * mm, "EnergiaLar - Sprint 4 - Avaliacao manual concluida")
    canvas.drawRightString(192 * mm, 9 * mm, f"Página {doc.page}")
    canvas.restoreState()


def make_table(rows, widths, header=True, font=6.8, repeatRows=1):
    converted = []
    for ri, row in enumerate(rows):
        converted.append([p(str(cell), "TableHeadCustom" if header and ri == 0 else "TableCustom") for cell in row])
    table = Table(converted, colWidths=widths, repeatRows=(repeatRows if header else 0), hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D8E0E7")),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D"))]
    for i in range(1 if header else 0, len(rows)):
        if i % 2 == 0:
            commands.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F5F8FA")))
    table.setStyle(TableStyle(commands))
    return table


def get_scores(mode: str):
    """Lê históricos sem misturar versões/execuções; para iterações seleciona um par comparável."""
    paths = sorted(RESULTS.glob(f"avaliacao_{mode}_*.csv"))
    legacy = RESULTS / f"avaliacao_{mode}.csv"
    if legacy.exists():
        paths.insert(0, legacy)
    by_run = defaultdict(list)
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                run_id = row.get("run_id") or path.stem
                by_run[(run_id, row.get("prompt_version", ""), row.get("model", ""))].append(row)

    aggregated = {}
    for key, rows in by_run.items():
        context, faith, relevancy, latency = [], [], [], []
        errors = sum(1 for row in rows if row.get("error"))
        for row in rows:
            for field, target in (("context_relevance_score", context), ("faithfulness_score", faith), ("answer_relevancy_score", relevancy)):
                try:
                    score = float(row.get(field, ""))
                    if 0 <= score <= 1:
                        target.append(score)
                except (ValueError, TypeError):
                    pass
            try:
                seconds = float(row.get("latency_seconds", ""))
                if seconds >= 0:
                    latency.append(seconds)
            except (ValueError, TypeError):
                pass
        citation_rows = [row for row in rows if str(row.get("citation_present", "")).lower() in {"true", "false"}]
        citation_coverage = (sum(1 for row in citation_rows if str(row.get("citation_present", "")).lower() == "true") / len(citation_rows)) if citation_rows else None
        aggregated[key] = {
            "context": mean(context) if context else None,
            "faith": mean(faith) if faith else None,
            "relevancy": mean(relevancy) if relevancy else None,
            "citation_coverage": citation_coverage,
            "citation_evaluated": len(citation_rows),
            "latency": mean(latency) if latency else None,
            "n_context": len(context), "n_faith": len(faith), "n_relevancy": len(relevancy),
            "n_rows": len(rows), "errors": errors,
            "structure_failures": sum(1 for row in rows if str(row.get("structure_valid", "")).lower() not in {"true", "1"}),
        }

    candidate_runs = defaultdict(lambda: defaultdict(set))
    for (run_id, prompt, model) in aggregated:
        candidate_runs[run_id][prompt].add(model)
    if mode == "iterations":
        candidates = []
        for run_id, prompts in candidate_runs.items():
            models = set.intersection(*(prompts.get(v, set()) for v in ("v1", "v2", "v3"))) if all(prompts.get(v) for v in ("v1", "v2", "v3")) else set()
            if models:
                for model in models:
                    counts = [aggregated[(run_id, v, model)]["n_rows"] for v in ("v1", "v2", "v3")]
                    candidates.append((1, min(counts), run_id, model, ("v1", "v2", "v3")))
            else:
                for older, newer in (("v1", "v2"), ("v2", "v3")):
                    for model in prompts.get(older, set()) & prompts.get(newer, set()):
                        count = min(aggregated[(run_id, older, model)]["n_rows"], aggregated[(run_id, newer, model)]["n_rows"])
                        candidates.append((0, count, run_id, model, (older, newer)))
        if candidates:
            _, _, selected_run, selected_model, versions = max(candidates, key=lambda item: (item[0], item[1], item[2]))
            return {(version, selected_model): aggregated[(selected_run, version, selected_model)] for version in versions}
    else:
        candidates = []
        for run_id, prompts in candidate_runs.items():
            selected_prompt = "v3" if len(prompts.get("v3", set())) >= 2 else "v2"
            models = prompts.get(selected_prompt, set())
            if len(models) >= 2:
                counts = [aggregated[(run_id, selected_prompt, model)]["n_rows"] for model in models]
                candidates.append((min(counts), run_id, selected_prompt, models))
        if candidates:
            _, selected_run, selected_prompt, selected_models = max(candidates, key=lambda item: (item[0], item[1]))
            return {(selected_prompt, model): aggregated[(selected_run, selected_prompt, model)] for model in sorted(selected_models)}

    if not aggregated:
        return {}
    latest_run = max(key[0] for key in aggregated)
    return {(prompt, model): value for (run_id, prompt, model), value in aggregated.items() if run_id == latest_run}


def get_prompt_pair_from_model_matrix(preferred_model: str = "gemma4:31b"):
    """Fallback: use the same model's v2/v3 pair from the scored 2-model matrix when iteration CSVs are unscored."""
    paths = sorted(RESULTS.glob("avaliacao_models_*.csv"))
    grouped = defaultdict(list)
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                run_id = row.get("run_id") or path.stem
                grouped[(run_id, row.get("prompt_version", ""), row.get("model", ""))].append(row)
    candidates = []
    for (run_id, prompt, model), rows in grouped.items():
        if prompt != "v2" or model != preferred_model:
            continue
        if (run_id, "v3", model) in grouped and rows and grouped[(run_id, "v3", model)]:
            scored = any(str(r.get("faithfulness_score", "")).strip() for r in rows + grouped[(run_id, "v3", model)])
            if scored:
                candidates.append((run_id, model))
    if not candidates:
        return {}
    run_id, model = max(candidates, key=lambda x: x[0])
    result = {}
    for prompt in ("v2", "v3"):
        rows = grouped[(run_id, prompt, model)]
        vals = {}
        for field, key in (("context_relevance_score", "context"), ("faithfulness_score", "faith"), ("answer_relevancy_score", "relevancy")):
            nums = []
            for row in rows:
                try:
                    n = float(row.get(field, ""))
                    if 0 <= n <= 1: nums.append(n)
                except (ValueError, TypeError): pass
            vals[key] = mean(nums) if nums else None
            vals["n_" + key] = len(nums)
        citation_rows = [r for r in rows if str(r.get("citation_present", "")).lower() in {"true", "false"}]
        vals["citation_coverage"] = sum(str(r.get("citation_present", "")).lower() == "true" for r in citation_rows) / len(citation_rows) if citation_rows else None
        vals["citation_evaluated"] = len(citation_rows)
        latencies=[]
        for row in rows:
            try: latencies.append(float(row.get("latency_seconds", "")))
            except (ValueError, TypeError): pass
        vals["latency"] = mean(latencies) if latencies else None
        vals["n_rows"] = len(rows)
        vals["errors"] = sum(1 for r in rows if r.get("error"))
        result[(prompt, model)] = vals
    return result


def fscore(value):
    return f"{value:.3f}" if value is not None else "Pendente"


def _coverage_label(value):
    coverage = value.get("citation_coverage") if value else None
    count = value.get("citation_evaluated", 0) if value else 0
    return f"{coverage * 100:.0f}% (n={count})" if coverage is not None else "Pendente"



def get_v1_pilot_score():
    """Load full manual v1 scores when available; otherwise retain the historical Q01 pilot."""
    full_files = sorted(RESULTS.glob("pontuacoes_manuais_v1_*.csv"))
    for path in reversed(full_files):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = [r for r in csv.DictReader(stream) if r.get("prompt_version") == "v1" and r.get("model") == "gemma4:31b"]
        if len(rows) >= 8:
            def vals(field):
                out = []
                for row in rows:
                    try:
                        x = float(row.get(field, ""))
                        if 0 <= x <= 1: out.append(x)
                    except (ValueError, TypeError):
                        pass
                return out
            context, faith, relevancy = vals("context_relevance_score"), vals("faithfulness_score"), vals("answer_relevancy_score")
            citation_rows = [r for r in rows if str(r.get("citation_present", "")).lower() in {"true", "false"}]
            citation_coverage = (sum(str(r.get("citation_present", "")).lower() == "true" for r in citation_rows) / len(citation_rows)) if citation_rows else None
            latencies = []
            for row in rows:
                try:
                    x = float(row.get("latency_seconds", ""))
                    if x >= 0: latencies.append(x)
                except (ValueError, TypeError):
                    pass
            return {
                "context": mean(context) if context else None,
                "faith": mean(faith) if faith else None,
                "relevancy": mean(relevancy) if relevancy else None,
                "citation_coverage": citation_coverage,
                "citation_evaluated": len(citation_rows),
                "latency": mean(latencies) if latencies else None,
                "n_context": len(context), "n_faith": len(faith), "n_relevancy": len(relevancy),
                "n_rows": len(rows), "errors": 0,
                "structure_failures": sum(1 for r in rows if str(r.get("structure_valid", "")).lower() not in {"true", "1"}),
                "pilot_only": False,
                "run_id": rows[0].get("run_id", path.stem),
            }

    path = RESULTS / "pontuacao_piloto_v1_q01.csv"
    if not path.exists():
        return None
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = [r for r in csv.DictReader(stream) if r.get("prompt_version") == "v1" and r.get("case_id") == "Q01" and r.get("model") == "gemma4:31b"]
    if not rows:
        return None
    row = rows[-1]
    def numeric(field):
        try:
            value = float(row.get(field, ""))
            return value if 0 <= value <= 1 else None
        except (ValueError, TypeError):
            return None
    return {
        "context": numeric("context_relevance_score"),
        "faith": numeric("faithfulness_score"),
        "relevancy": numeric("answer_relevancy_score"),
        "citation_coverage": 1.0 if row.get("citation_present", "").lower() == "true" else 0.0 if row.get("citation_present", "").lower() == "false" else None,
        "citation_evaluated": 1 if row.get("citation_present", "").lower() in {"true", "false"} else 0,
        "latency": float(row.get("latency_seconds", "0") or 0),
        "n_context": int(numeric("context_relevance_score") is not None),
        "n_faith": int(numeric("faithfulness_score") is not None),
        "n_relevancy": int(numeric("answer_relevancy_score") is not None),
        "n_rows": 1, "errors": 0, "structure_failures": 0,
        "pilot_only": True,
    }


def build_report_pdf():
    REPORT_PDF.parent.mkdir(parents=True, exist_ok=True)
    iter_scores = get_scores("iterations")
    model_scores = get_scores("models")
    matrix_pair = get_prompt_pair_from_model_matrix("gemma4:31b")
    if matrix_pair and all(matrix_pair.get((v, "gemma4:31b"), {}).get("faith") is not None for v in ("v2", "v3")):
        iter_scores = matrix_pair
    v1_pilot = get_v1_pilot_score()
    if v1_pilot and not iter_scores.get(("v1", "gemma4:31b"), {}).get("n_faith", 0):
        iter_scores[("v1", "gemma4:31b")] = v1_pilot
    manual_path = ROOT / "data" / "knowledge_base" / "00_manual_oficial_goodwe_hca_g2_en.pdf"
    if manual_path.is_file():
        compatibility_path = ROOT / "data" / "knowledge_base" / "00b_compatibilidade_goodwe_ev_hca_g2_en.pdf"
        if compatibility_path.is_file():
            manual_status = "O manual HCA G2 em inglês e a lista oficial de compatibilidade estão presentes; confirmar que o índice Chroma foi reconstruído após sua inclusão."
        else:
            manual_status = "O manual oficial GoodWe HCA G2 em inglês está presente; a lista oficial de compatibilidade complementar ainda não foi encontrada. Reconstrua o índice após incluir os PDFs disponíveis."
    else:
        manual_status = "O pacote de projeto analisado inclui os dois PDFs oficiais GoodWe. Em uma instalação limpa ou após atualização, baixe/valide os PDFs com scripts/baixar_manual_oficial.ps1 e reconstrua o índice antes da avaliação; o resumo Markdown não substitui o manual oficial."
    doc = SimpleDocTemplate(str(REPORT_PDF), pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=15*mm, bottomMargin=19*mm, title="Relatório de evolução - EnergiaLar Sprint 4")
    story = []

    # Página 1
    story += [
        p("Relatório de evolução do projeto", "TitleCustom"),
        p("EnergiaLar | Sprint 4 | FIAP x GoodWe Brasil | Prompt and Artificial Intelligence | 2026.2", "SubTitleCustom"),
        p("Relatório baseado em fallback manual; limitações técnicas e evidências disponíveis são declaradas de forma explícita.", "CalloutCustom"),
        p("1. Resumo da evolução", "H1Custom"),
        p("A Sprint 3 do EnergiaLar manteve uma cadeia conversacional LCEL com memória por sessão, validação Pydantic v2, prompts externos e avaliação de modelos. A Sprint 4 preserva essa base e acrescenta uma camada documental RAG com ChromaDB persistente, prompts RAG versionados, citações visíveis, interface Streamlit e avaliação de fidelidade e relevância.", "BodyCustom"),
        p("O RAG não substitui o assistente conversacional da Sprint 3 nem cria ligação com um carregador físico. Ele acrescenta uma camada documental para responder com base em fontes recuperadas, citações visíveis e recusa quando faltar evidência.", "BodyCustom"),
        p("Validação funcional registrada no workspace Windows: 48 testes aprovados após correções Q04/Q05. A v1 foi pontuada manualmente nos oito casos em 23/10/2026 (run_id 20261023_003912_871419): contexto médio 0,857 (n=7; revisão manual dos chunks completos), faithfulness/relevância 0,938/0,938, citações 7/7 e estrutura válida 8/8. V1→v2 caiu 0,031; v2→v3 subiu +0,094 para 1,000/1,000. Scores são fallback manual, não RAGAS.", "BodyCustom"),
        p("Referência técnica histórica da versão pública Sprint 3: nos cinco casos happy-path comparáveis, o arquivo sprint3_results.json registra 192,6 tokens médios, 9,356 s de latência média e saída estruturada válida em 5/5 casos. Os campos de avaliação manual continuam pendentes; esses valores não são scores de qualidade. A comparação da Sprint 2 registrava cinco casos como Adequada, sem tokens/latência.", "BodyCustom"),
        p("2. Pipeline RAG", "H1Custom"),
        p("Documentos em data/knowledge_base -> PyMuPDFLoader para PDFs / TextLoader para Markdown e TXT / CSVLoader para CSV -> filtro heurístico de linhas maliciosas -> RecursiveCharacterTextSplitter -> nomic-embed-text via Ollama local (desvio literal Cloud documentado) -> ChromaDB persistente -> retriever top-k -> prompt RAG versionado v1/v2/v3 -> gemma4:31b no Ollama Cloud -> JSON validado por Pydantic v2 -> resposta e fontes no Streamlit.", "BodyCustom"),
        p("Configuração usada: chunk_size=800 caracteres, overlap=120, top_k=8, limiar de relevância=0,15, temperature=0, top_p=0,9 e max_tokens=600. O limiar é configurável e precisa ser validado pelo eval set; não é uma garantia universal.", "BodyCustom"),
        PageBreak(),
    ]

    # Página 2
    story += [
        p("3. Base de conhecimento e trade-offs", "H1Custom"),
        p("O pacote analisado inclui os dois PDFs oficiais GoodWe, além de folha de dados, FAQ, protocolo-modelo de condomínio não normativo, leis paulistas com links oficiais, preços didáticos simulados e componentes tarifários publicados pela Enel SP (vigência indicada desde 04/07/2026, não equivalem à fatura total). O manual continua obrigatório para liberar a indexação. " + manual_status, "BodyCustom"),
        p("O chunk de 800 caracteres procura preservar uma unidade curta de informação; overlap de 120 preserva continuidade em limites de blocos. Aumentar chunk pode juntar assuntos diferentes; diminuir demais pode separar ressalvas de segurança. A escolha inicial deve ser validada por fidelidade e relevância medidas, não apenas por respostas fluentes.", "BodyCustom"),
        p("4. Segurança e grounding", "H1Custom"),
        p("Os prompts v2/v3 distinguem explicitamente contexto de instruções, mandam ignorar tentativas de prompt injection contidas nos documentos, pedem recusa fora do escopo, exigem o contrato JSON de Pydantic v2 e proíbem inventar especificações, compatibilidades, tarifas e dimensionamentos elétricos. O carregador filtra padrões conhecidos de instruções maliciosas e a saída tem um bloqueio heurístico simples para padrões semelhantes a credenciais. Esses mecanismos reduzem riscos conhecidos, mas não são uma prova formal de segurança.", "BodyCustom"),
        p("Toda consulta com contexto útil mostra nome da fonte e página do PDF, quando disponível. Se nenhum chunk ultrapassa o limiar, a aplicação responde com uma recusa e informa que a base não deu suporte suficiente.", "BodyCustom"),
        p("5. Problemas encontrados e soluções", "H1Custom"),
        make_table([
            ["Problema", "Decisão tomada e motivo"],
            ["Base da Sprint 3 era conversacional, sem busca vetorial", "Preservar LCEL, prompts externos, memória por sessão e o schema Pydantic; acrescentar uma camada documental separada para RAG."],
            ["Risco de o modelo inventar dados ou seguir texto malicioso", "Prompt v2 com contexto não confiável, filtro inicial de linhas suspeitas, recusa por falta de evidência e caso de teste de injection."],
            ["Tarifas e regras do condomínio podem ser interpretadas como oficiais", "Separar referência oficial de exemplo simulado e rotular explicitamente o protocolo de condomínio como orientativo."],
            ["Q04 omitia o art. 2º da lei estadual em uma pergunta ampla", "Busca complementar dirigida ao art. 2º, validação dos termos artigo/capacidade mínima/instalação futura e regra no prompt v3 para cobrir o ponto quando está no contexto."],
        ], [48*mm, 122*mm]),
        PageBreak(),
    ]

    # Página 3
    default_score = {"context": None, "faith": None, "relevancy": None, "citation_coverage": None, "citation_evaluated": 0, "n_context": 0, "n_faith": 0, "n_relevancy": 0, "n_rows": 0}
    scores_by_version = {version: next((value for key, value in iter_scores.items() if key[0] == version), default_score.copy()) for version in ("v1", "v2", "v3")}
    v1, v2, v3 = scores_by_version["v1"], scores_by_version["v2"], scores_by_version["v3"]
    d12_f = v2["faith"] - v1["faith"] if v1.get("faith") is not None and v2.get("faith") is not None else None
    d12_r = v2["relevancy"] - v1["relevancy"] if v1.get("relevancy") is not None and v2.get("relevancy") is not None else None
    d12_c = v2["context"] - v1["context"] if v1.get("context") is not None and v2.get("context") is not None else None
    d23_f = v3["faith"] - v2["faith"] if v2.get("faith") is not None and v3.get("faith") is not None else None
    d23_r = v3["relevancy"] - v2["relevancy"] if v2.get("relevancy") is not None and v3.get("relevancy") is not None else None
    d23_c = v3["context"] - v2["context"] if v2.get("context") is not None and v3.get("context") is not None else None
    iteration_rows = [
        ["Indicador", "Sprints 1/2 (versão original)", "Sprint 4 v1", "Sprint 4 v2", "Sprint 4 v3"],
        ["Arquitetura", "Versão original sem RAG vetorial; detalhes históricos limitados.", "RAG separado; Chroma + UI.", "Mesmo pipeline; prompt atualizado.", "Mesmo pipeline; iteração extra."],
        ["Grounding/citação", "Citação documental por chunk/página não registrada.", "Cobertura 100% (7/7).", "Cobertura 100% (7/7).", "Cobertura 100% (7/7)."],
        ["Qualidade do contexto (0-1)", "N/A: sem RAG.", f"{fscore(v1['context'])} (n={v1['n_context']}; auditado)", f"{fscore(v2['context'])} (n={v2['n_context']}; mesmos chunks)", f"{fscore(v3['context'])} (n={v3['n_context']}; mesmos chunks)"],
        ["Faithfulness (0-1)", "N/A: sem RAG.", f"{fscore(v1['faith'])} (n={v1['n_faith']})", f"{fscore(v2['faith'])} (n={v2['n_faith']})", f"{fscore(v3['faith'])} (n={v3['n_faith']})"],
        ["Answer relevancy (0-1)", "N/A: sem RAG.", f"{fscore(v1['relevancy'])} (n={v1['n_relevancy']})", f"{fscore(v2['relevancy'])} (n={v2['n_relevancy']})", f"{fscore(v3['relevancy'])} (n={v3['n_relevancy']})"],
        ["Citações presentes (%)", "Não coletado no baseline.", _coverage_label(v1), _coverage_label(v2), _coverage_label(v3)],
        ["Delta v2 - v1", "N/A", "N/A", f"Faith={fscore(d12_f)}; Relev.={fscore(d12_r)}; Contexto={fscore(d12_c)}", "N/A"],
        ["Delta v3 - v2", "N/A", "N/A", "N/A", f"Faith={fscore(d23_f)}; Relev.={fscore(d23_r)}; Contexto={fscore(d23_c)}"],
    ]
    story += [
        p("6. Tabela de comparativo antes/depois", "H1Custom"),
        p("A v1 foi pontuada nos oito casos; a rubrica manual de 0-1 não é RAGAS. Q04 e Q05 receberam 0,75 em faithfulness/relevância por omissões secundárias; Q07 recebeu 1,00/1,00 conforme a rubrica de segurança. A auditoria dos chunks completos pontuou contexto Q01=0,75, Q02=1,00, Q03=1,00, Q04=1,00, Q05=0,75, Q07=0,75 e Q08=0,75; Q06 é N/A. A média do contexto é 0,857; há ruído de chunks adicionais, e a nota não é RAGAS.", "BodyCustom"),
        make_table(iteration_rows, [30*mm, 35*mm, 35*mm, 35*mm, 32*mm]),
        p("Deltas medidos: v1→v2 = -0,031 em faithfulness/relevância e 0,000 em contexto; v2→v3 = +0,094 em faithfulness/relevância e 0,000 em contexto. A média do contexto fica em 0,857 (n=7) nas três versões, pois os chunks recuperados por pergunta são iguais nos registros avaliados.", "SmallCustom"),
        Spacer(1, 5),
        p("7. Comparação de modelos no prompt v3", "H1Custom"),
    ]
    model_rows = [["Modelo (v3)", "Faithfulness", "Answer relevancy", "Latência (s)", "Casos", "Falhas JSON"]]
    for (prompt_version, model), vals in sorted(model_scores.items()):
        if prompt_version != "v3":
            continue
        latency_text = f"{vals['latency']:.2f}" if vals.get("latency") is not None else "Pendente"
        model_rows.append([model, fscore(vals["faith"]), fscore(vals["relevancy"]), latency_text, str(vals["n_rows"]), str(vals.get("structure_failures", 0))])
    if len(model_rows) == 1:
        model_rows.extend([
            ["gemma4:31b", "Pendente", "Pendente", "Pendente", "Pendente", "Pendente"],
            ["gpt-oss:20b", "Pendente", "Pendente", "Pendente", "Pendente", "Pendente"],
        ])
    story.append(make_table(model_rows, [32*mm, 29*mm, 31*mm, 26*mm, 22*mm, 22*mm]))
    story += [
        Spacer(1, 6),
        p("A rubrica manual de 0 a 1 está em evals/manual_rubric.md. As notas são fallback manual, não RAGAS. O GPT-OSS teve cinco falhas JSON no total da matriz (3 em v2, 2 em v3); as falhas foram mantidas no agregado.", "SmallCustom"),
        PageBreak(),
    ]

    # Página 4
    story += [
        p("8. Parâmetros e reprodutibilidade", "H1Custom"),
        make_table([
            ["Item", "Configuração registrada"],
            ["Embeddings Windows", "nomic-embed-text em Ollama local; desvio literal de Ollama Cloud registrado"],
            ["Alternativa Colab", "nomic-ai/nomic-embed-text-v1.5 executado no runtime cloud do Colab; chat no Ollama Cloud; não é endpoint de embeddings Ollama Cloud"],
            ["Modelos comparados", "gemma4:31b (recomendado, prompt v3) e gpt-oss:20b (5 falhas JSON em 16 saídas)"],
            ["temperature / top_p / max_tokens", "0.0 / 0.9 / 600"],
            ["Recuperação", "top_k=8; limiar inicial=0.15; expansão dirigida da evidência legal para Q04"],
            ["Chunking", "800 caracteres; overlap=120"],
            ["Reprodução", "`python -m src.rag.build_index --force`; `python -m evals.run_eval --mode iterations --model gemma4:31b --interactive`; `python -m evals.run_eval --mode models --models gemma4:31b gpt-oss:20b --interactive`"],
        ], [46*mm, 124*mm]),
        p("A configuração funcional mantém `gemma4:31b` no chat Cloud e usa `nomic-embed-text` local para embeddings, pois o endpoint Cloud retornou 401. Isso diverge literalmente do requisito de embeddings Cloud e está documentado; não declarar conformidade integral.", "BodyCustom"),
        p("9. Equipe e divisão de trabalho", "H1Custom"),
        p("A implementação e a avaliação documentadas nesta versão foram executadas por Kaique. Para manter o registro honesto, as atribuições dos demais integrantes aparecem como revisões propostas e pendentes, não como trabalho concluído.", "BodyCustom"),
        make_table([
            ["Integrante", "RM", "Contribuição confirmada / revisão proposta"],
            ["Renan Eskildssen", "571097", "Contribuição nesta versão não confirmada; revisão de proveniência documental ainda não confirmada."],
            ["Lucas Barros", "571528", "Contribuição nesta versão não confirmada; revisão da comparação de modelos e parâmetros pendente."],
            ["Kaique Da Silva Assis", "572718", "Implementação RAG, Q04/Q05, prompts, testes, avaliação manual e documentação."],
            ["Andre Debiazzi Baldi Negrini", "569062", "Contribuição nesta versão não confirmada; revisão de guardrails e prompt injection pendente."],
            ["Vinicius Cristal de Oliveira", "572049", "Contribuição nesta versão não confirmada; teste final da interface/citações pendente."],
        ], [43*mm, 20*mm, 107*mm]),
        Spacer(1, 7),
        p("A v1 foi pontuada em Q01-Q08 e incorporada ao comparativo: v1=0,938, v2=0,906 e v3=1,000 nas duas métricas de resposta. O contexto foi auditado dos chunks integrais: 0,857 nos sete casos recuperáveis (Q06=N/A). O notebook Colab usa Nomic Embed Text v1.5 no runtime hospedado do Colab; não é o endpoint gerenciado de embeddings Ollama Cloud.", "CalloutCustom"),
        p("Fontes oficiais e rastreabilidade, revisão documental em 23/10/2026: GoodWe Brasil - downloads HCA G2 (https://br.goodwe.com/download-hca-g2-series) e ficha técnica (https://br.goodwe.com/Api/downloadFile?id=3931&mid=60&type=1); ALESP, Lei 18.403/2026 (https://al.sp.gov.br/repositorio/legislacao/lei/2026/lei-18403-18.02.2026.html); Prefeitura de São Paulo, Lei 17.336/2020 (https://legislacao.prefeitura.sp.gov.br/lei-17336-de-30-de-marco-de-2020); Enel SP, tarifa vigente desde 04/07/2026 (https://www.enel.com.br/pt-saopaulo/Para_Voce/tarifa-energia-eletrica.html); Ollama Cloud e API de embeddings (https://docs.ollama.com/cloud; https://docs.ollama.com/api/embed; https://github.com/ollama/ollama/issues/14496; https://github.com/ollama/ollama/issues/17129); registro oficial de gpt-oss:20b e preços (https://ollama.com/library/gpt-oss%3A20b-cloud). Referências adicionais e escopo das afirmações estão em docs/REVISAO_FONTES_EXTERNAS.md. Valores didáticos não são tarifas oficiais.", "SmallCustom"),
    ]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main():
    build_report_pdf()
    print(f"Relatório de evolução (prévia): {REPORT_PDF}")


if __name__ == "__main__":
    main()

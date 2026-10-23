"""Guardrails básicos para documentos recuperados e respostas."""
from __future__ import annotations
import re
import unicodedata

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|preceding)\s+instructions", re.I),
    re.compile(r"ignore\s+all\s+instructions", re.I),
    re.compile(r"ignore\s+(todas\s+)?as\s+instru[cç][oõ]es\s+(anteriores|pr[eé]vias)", re.I),
    re.compile(r"desconsidere\s+(todas\s+)?as\s+instru[cç][oõ]es\s+(anteriores|pr[eé]vias)", re.I),
    re.compile(r"\b(ignore|desconsidere|esque[cç]a)\b.{0,80}\b(instru[cç][oõ]es|regras|prompt|sistema)\b", re.I),
    re.compile(r"reveal\s+(the\s+)?(api\s*key|secret|credentials?|system prompt)", re.I),
    re.compile(r"revele\s+(a\s+)?(chave\s+(?:da?\s*)?api|credencial|segredo|prompt\s+do\s+sistema)", re.I),
    re.compile(r"\b(reveal|show|expose|print)\b.{0,80}\b(api key|secret|credentials?|environment variables|system prompt)\b", re.I),
    re.compile(r"\b(revele|mostre|exponha|imprima)\b.{0,80}\b(chave|credencial|token|segredo|vari[aá]veis? de ambiente)\b", re.I),
    re.compile(r"you\s+are\s+now\s+(the\s+)?system", re.I),
    re.compile(r"alter(e|ar)\s+(seu\s+)?papel\s+para\s+administrador", re.I),
    re.compile(r"print\s+(the\s+)?environment\s+variables", re.I),
    re.compile(r"imprima\s+(as\s+)?vari[aá]veis\s+de\s+ambiente", re.I),
]
SECRET_PATTERNS = [
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"(?i)\bsk-[A-Za-z0-9]{16,}"),
    re.compile(r"(?i)\b(?:OLLAMA[_-])?API[_-]?KEY\s*[:=]\s*[A-Za-z0-9._-]{16,}"),
    re.compile(r"(?i)\bOLLAMA[_-]?KEY\s*[:=]\s*[A-Za-z0-9._-]{16,}"),
]

SECRET_REDACTION_PATTERNS = [
    re.compile(r"(?i)(\bBearer\s+)[A-Za-z0-9._-]{20,}"),
    re.compile(r"(?i)(\bsk-)[A-Za-z0-9]{16,}"),
    re.compile(r"(?i)(\b(?:OLLAMA[_-])?API[_-]?KEY\s*[:=]\s*)[A-Za-z0-9._-]{16,}"),
    re.compile(r"(?i)(\bOLLAMA[_-]?KEY\s*[:=]\s*)[A-Za-z0-9._-]{16,}"),
]


SCOPE_HINTS = (
    "energia", "energetic", "eficiencia", "consumo", "recarga", "carregador",
    "carregamento", "veiculo", "carro eletrico", "hca", "goodwe", "inversor",
    "bateria", "fotovolta", "solar", "sems", "kwh", "kw", "quilowatt",
    "tarifa", "fatura", "condominio", "sessao de carregamento", "potencia",
    "distribuidora", "electric vehicle", "ev charger", "charging", "charger",
    "battery", "inverter", "solar energy", "energy efficiency", "tariff",
    "enel",
    "aneel",
    "tusd",
    "te-bvd",
    "mwh",
    "b1 residencial",
    "residencial convencional",
    "tarifaria",
    "componente tarifario",
)


def is_out_of_scope_question(question: str) -> bool:
    """Recusa cedo perguntas claramente alheias ao domínio documentado.

    É um filtro conservador por termos: ele não substitui a relevância semântica,
    mas evita usar o modelo para responder perguntas evidentemente fora do tema.
    """
    normalized = unicodedata.normalize("NFKD", str(question or "").casefold())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return not any(term in normalized for term in SCOPE_HINTS)


def is_injection_line(line: str) -> bool:
    return any(pattern.search(line) for pattern in INJECTION_PATTERNS)


def sanitize_user_question(question: str) -> tuple[str, bool]:
    """Remove whole suspicious clauses before retrieval/model invocation.

    Sentence/semicolon boundaries are used conservatively: if a clause contains
    an instruction to override rules or reveal secrets, that clause is discarded.
    Safe independent clauses are retained (for example, the product question in
    a message that first asks to reveal an API key). The flag records that a
    security intervention occurred for UI/evaluation transparency.
    """
    raw = str(question or "").strip()
    if not raw:
        return "", False
    clauses = [part.strip() for part in re.split(r"(?<=[.!?])\s+|[;\n]+", raw) if part.strip()]
    safe_clauses = [part for part in clauses if not is_injection_line(part)]
    changed = len(safe_clauses) != len(clauses)
    return " ".join(safe_clauses).strip(), changed


def sanitize_untrusted_text(text: str) -> str:
    """Remove linhas que aparentam tentar controlar o modelo; mantém o conteúdo factual ao redor."""
    safe_lines = [line for line in text.splitlines() if not is_injection_line(line)]
    return "\n".join(safe_lines).strip()


def contains_possible_secret(text: str) -> bool:
    return any(pattern.search(text or "") for pattern in SECRET_PATTERNS)


def redact_sensitive_text(text: str, secret: str = "") -> str:
    """Redige a chave configurada quando uma exceção/diagnóstico a reproduz."""
    value = str(text or "")
    if secret:
        value = value.replace(secret, "[CHAVE REDIGIDA]")
    for pattern in SECRET_REDACTION_PATTERNS:
        value = pattern.sub(lambda match: match.group(1) + "[CHAVE REDIGIDA]", value)
    return value

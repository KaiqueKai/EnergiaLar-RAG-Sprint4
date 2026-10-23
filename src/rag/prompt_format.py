"""Parser puro para separar instruções de sistema e mensagem do usuário."""

MARKER = "\n--- HUMAN ---\n"


def split_prompt(text: str) -> tuple[str, str]:
    if MARKER not in text:
        raise ValueError("Prompt inválido: inclua uma linha --- HUMAN --- para separar system e human.")
    system, human = text.split(MARKER, 1)
    if not system.strip() or not human.strip():
        raise ValueError("Prompt inválido: as seções SYSTEM e HUMAN não podem estar vazias.")
    return system.strip(), human.strip()

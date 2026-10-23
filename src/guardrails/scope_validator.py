import re

TERMOS_GOODWE = [
    "goodwe", "carregador", "carregadores", "carregamento", "recarga",
    "estação de carregamento", "estacao de carregamento", "veículo elétrico",
    "veiculo eletrico", "veículos elétricos", "veiculos eletricos",
    "carro elétrico", "carro eletrico", "ev charger", "wallbox", "energia",
    "consumo", "consumo energético", "consumo energetico", "kwh", "kw",
    "potência", "potencia", "tarifa", "demanda", "sessão de carga",
    "sessao de carga", "eficiência", "eficiencia", "eficiência energética",
    "eficiencia energetica", "eficiência operacional", "eficiencia operacional",
    "indicadores", "monitorar", "monitoramento", "falhas", "falha",
    "manutenção", "manutencao", "manutenção preventiva", "manutencao preventiva",
]

def validar_escopo(pergunta: str) -> bool:
    texto = (pergunta or "").lower().strip()
    if not texto:
        return False
    return any(re.search(re.escape(termo), texto) for termo in TERMOS_GOODWE)

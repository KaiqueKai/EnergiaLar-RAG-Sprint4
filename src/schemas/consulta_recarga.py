from typing import Optional
from pydantic import BaseModel, Field, field_validator

class ConsultaRecarga(BaseModel):
    estado_carregador: str = Field(description="Estado do carregador ou da recarga.")
    potencia_kw: Optional[float] = Field(default=None, description="Potência de carregamento em kW, quando informada.")
    faturamento_reais: Optional[float] = Field(default=None, description="Valor em reais relacionado à cobrança, quando informado.")
    resposta: str = Field(description="Resposta final para o usuário.")

    @field_validator("estado_carregador")
    @classmethod
    def validar_estado(cls, valor):
        valor = valor.strip()
        estados_validos = ["carregando", "pausado", "finalizado", "desconectado", "erro", "desconhecido"]
        return valor.lower() if valor.lower() in estados_validos else "desconhecido"

    @field_validator("potencia_kw", "faturamento_reais")
    @classmethod
    def validar_valores(cls, valor):
        if valor is not None and valor < 0:
            raise ValueError("O valor não pode ser negativo.")
        return valor

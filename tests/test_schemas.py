import pytest
from pydantic import ValidationError
from src.schemas.consulta_recarga import ConsultaRecarga

def test_schema_aceita_estado_valido():
    obj=ConsultaRecarga(estado_carregador="carregando",potencia_kw=7.4,faturamento_reais=None,resposta="Sessão iniciada.")
    assert obj.estado_carregador == "carregando"
    assert obj.potencia_kw == 7.4

def test_estado_desconhecido_normaliza_estado_invalido():
    obj=ConsultaRecarga(estado_carregador="Disponível",potencia_kw=None,faturamento_reais=None,resposta="Sem evidência.")
    assert obj.estado_carregador == "desconhecido"

def test_schema_rejeita_valores_negativos():
    with pytest.raises(ValidationError):
        ConsultaRecarga(estado_carregador="carregando",potencia_kw=-7,faturamento_reais=None,resposta="Inválido.")

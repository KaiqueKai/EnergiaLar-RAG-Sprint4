# Arquitetura

## Fluxo principal

```text
Pergunta do usuário
        ↓
ChatPromptTemplate
        ↓
MessagesPlaceholder (memória)
        ↓
LCEL: prompt | ChatOllama
        ↓
Resposta JSON do modelo Cloud
        ↓
Parser JSON
        ↓
Pydantic (ConsultaRecarga)
        ↓
Resposta estruturada
```

## Responsabilidades

### `src/chatbot.py`

Centraliza a construção da cadeia LCEL, a memória por sessão e a normalização/validação da saída.

### `src/schemas/consulta_recarga.py`

Define o contrato de dados esperado pela aplicação.

### `src/config.py`

Centraliza caminhos, nomes dos modelos e configurações para evitar strings duplicadas espalhadas pelo projeto.

### `prompts/`

Mantém os prompts fora do código Python, facilitando manutenção e revisão.

### `evals/`

Contém os casos de teste e os scripts de medição/comparação.

### `tests/`

Valida componentes locais sem consumir créditos do Ollama Cloud.

## Memória

A memória é mantida por `session_id`. Sessões diferentes possuem históricos independentes. Isso permite avaliar conversas isoladas sem misturar contextos.

## Pydantic

A classe `ConsultaRecarga` garante que a resposta final possua os quatro campos definidos pela atividade e que `resposta` não seja vazia.

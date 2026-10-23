# Sprint 3 — Assistente de Eficiência Energética

Projeto acadêmico da Sprint 3 com foco em um chatbot para apoio à operação e eficiência energética de estações de recarga de veículos elétricos.

## Objetivo

A Sprint 3 organiza o projeto em uma arquitetura separada por responsabilidades e adiciona uma camada de avaliação técnica. A aplicação utiliza LCEL para compor a cadeia, memória por sessão para manter contexto e Pydantic para validar a estrutura final das respostas.

A avaliação compara a implementação da Sprint 3 com um baseline de referência e mede tokens, latência e validade estrutural.

## Arquitetura

```text
sprint-3-jorge/
├── README.md
├── main.py
├── requirements.txt
├── .gitignore
├── prompts/
│   ├── system_prompt.txt
│   └── baseline_prompt.txt
├── docs/
│   ├── arquitetura.md
│   ├── avaliacao.md
│   └── execucao.md
├── evals/
│   ├── __init__.py
│   ├── casos_teste.json
│   ├── run_baseline.py
│   ├── model_comparison.py
│   └── comparar_sprint2_sprint3.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── chatbot.py
│   └── schemas/
│       ├── __init__.py
│       └── consulta_recarga.py
└── tests/
    ├── __init__.py
    ├── test_chatbot.py
    └── test_schemas.py
```

## Modelos

A execução deste projeto usa somente modelos Cloud através do Ollama:

- `gemma4:31b-cloud`
- `gpt-oss:120b-cloud`

Não há download nem execução de modelo local no projeto.

## Principais requisitos técnicos

- Python 3.14
- LangChain / LCEL
- Ollama Cloud via cliente Ollama
- Pydantic v2
- Memória por sessão
- Avaliação automática
- Testes unitários sem necessidade de chamar o modelo

## Execução

Na raiz do projeto:

```bash
python -m evals.run_baseline
python -m evals.model_comparison
python -m evals.comparar_sprint2_sprint3
```

Para executar os testes unitários:

```bash
python -m pytest
```

Para uma demonstração manual:

```bash
python main.py
```

## Observação sobre avisos do LangChain

A aplicação pode exibir um `LangChainDeprecationWarning` relacionado a `RunnableWithMessageHistory`. Isso é um aviso de API futura e não constitui, por si só, uma falha de execução. A memória por sessão permanece implementada para atender ao requisito da atividade.

## Resultados

Os arquivos de resultado são gerados automaticamente na pasta `evals/`:

- `sprint2_baseline.json`
- `model_comparison_results.json`

Esses arquivos não são incluídos no repositório base porque dependem da execução realizada no computador do grupo e devem registrar os valores reais obtidos no teste.

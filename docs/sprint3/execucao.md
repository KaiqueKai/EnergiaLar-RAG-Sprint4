# Execução

## Pré-requisitos

1. Python instalado e funcionando.
2. Dependências instaladas com `pip install -r requirements.txt`.
3. Ollama instalado e autenticado para uso Cloud.
4. A conta deve ter acesso ao uso dos modelos Cloud selecionados.
5. Não é necessário baixar modelos locais.

## Testes unitários

```bash
python -m pytest
```

## Baseline

```bash
python -m evals.run_baseline
```

Esse comando gera `evals/sprint2_baseline.json`.

## Comparação de modelos

```bash
python -m evals.model_comparison
```

Esse comando executa os cinco casos em:

- `gemma4:31b-cloud`
- `gpt-oss:120b-cloud`

O segundo modelo é Cloud e deve ser acessado via Ollama, sem baixar os pesos localmente. O catálogo oficial do Ollama disponibiliza o identificador `gpt-oss:120b-cloud`. 

## Comparação Sprint 2 × Sprint 3

```bash
python -m evals.comparar_sprint2_sprint3
```

O comando depende da existência dos dois JSON de resultados.

## Demonstração

```bash
python main.py
```

A demonstração usa o primeiro modelo Cloud configurado e mantém uma sessão de memória durante a interação.

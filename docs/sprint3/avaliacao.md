# Avaliação

A avaliação usa os mesmos cinco casos para os modelos da Sprint 3.

## Métricas

### Tokens

A quantidade de tokens da resposta é contada com `tiktoken` usando a codificação `cl100k_base`. O valor é usado como uma métrica consistente entre as execuções; ele não representa necessariamente a tokenização interna específica de cada modelo.

### Latência

É medido o tempo entre o início da chamada e o recebimento da resposta do modelo.

### Estrutura Pydantic

Após o retorno, a resposta é convertida para `ConsultaRecarga`. Uma conversão bem-sucedida é registrada como estrutura válida.

### Robustez do avaliador

Falha em um modelo ou em um caso não encerra toda a avaliação. O erro é registrado no JSON e os demais casos continuam.

## Arquivos gerados

`evals/sprint2_baseline.json` registra o baseline.

`evals/model_comparison_results.json` registra os resultados da comparação dos modelos da Sprint 3.

## Interpretação

Os números devem ser tratados como resultados daquela execução específica. Latência e disponibilidade de um serviço Cloud podem variar entre execuções.

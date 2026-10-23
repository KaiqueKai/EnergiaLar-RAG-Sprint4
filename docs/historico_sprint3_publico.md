# Evidências históricas do repositório público EnergiaLar

Consulta realizada em 21/10/2026 ao repositório do grupo: https://github.com/KaiqueKai/EnergiaLar.

## Resultado Sprint 3 publicado

O arquivo público `evals/sprint3_results.json` registra uma execução de 20/09/2026 com 14 casos. Os cinco casos `happy_path` comparáveis ao baseline da Sprint 2 registram estes valores técnicos:

| Caso | Tokens da resposta | Latência (s) | Estrutura válida |
|---|---:|---:|---|
| EV-01 | 215 | 16,10 | Sim |
| EV-02 | 138 | 6,47 | Sim |
| EV-03 | 45 | 5,14 | Sim |
| EV-04 | 433 | 10,95 | Sim |
| EV-05 | 132 | 8,12 | Sim |
| **Média / total** | **192,6** | **9,356** | **5/5 válidas** |

Cálculo da média de tokens: (215 + 138 + 45 + 433 + 132) / 5 = 192,6. Cálculo da latência média: (16,10 + 6,47 + 5,14 + 10,95 + 8,12) / 5 = 9,356 segundos.

**Limite importante:** os campos de avaliação manual nesse JSON estão marcados como `PREENCHER_MANUALMENTE`. Os números acima são somente tokens, latência e validade estrutural; não representam `faithfulness`, `answer_relevancy` nem uma nota de qualidade inventada.

## Baseline Sprints 1/2

O script público `evals/comparar_sprint2_sprint3.py` lista cinco casos happy-path da Sprint 2 com avaliação registrada como “Adequada”. Ele explicita que a Sprint 2 não tinha tokens nem latência registrados, portanto esses números não devem ser inferidos. Para a tabela obrigatória do relatório, métricas RAG (`faithfulness`, `answer_relevancy`, busca vetorial e citação documental) são N/A na versão sem RAG, não zero.

## Fontes para auditoria

- Repositório público EnergiaLar: https://github.com/KaiqueKai/EnergiaLar
- Resultados públicos da Sprint 3: https://raw.githubusercontent.com/KaiqueKai/EnergiaLar/main/evals/sprint3_results.json
- Comparativo Sprint 2 × Sprint 3: https://raw.githubusercontent.com/KaiqueKai/EnergiaLar/main/evals/comparar_sprint2_sprint3.py

Este histórico deve ser revalidado se os arquivos do branch `main` forem atualizados pelo grupo.

# Pontuação piloto — prompt RAG v1

**Amostra:** run `20261021_141337_594341`, caso Q01, modelo `gemma4:31b`, n=1.

| Métrica | Nota | Justificativa |
|---|---:|---|
| Relevância do contexto | 1,00 | O contexto recuperado contém as três potências e os respectivos modelos HCA G2 solicitados. |
| Faithfulness | 1,00 | A resposta repete os valores presentes no contexto, sem acrescentar uma especificação não sustentada. |
| Answer relevancy | 1,00 | Responde diretamente à pergunta e inclui os três modelos pedidos. |
| Presença de citação | Sim | A resposta usa [1] e lista a fonte recuperada. |
| JSON estruturado | Válido | Os campos do contrato foram aceitos na execução registrada. |

**Limite:** há somente Q01 pontuada para v1. A nota 1,00 é um resultado piloto individual, não uma média do conjunto de oito perguntas. Não deve ser usada no cálculo de delta frente às médias completas de v2/v3. O ganho quantitativo comunicado no relatório continua sendo v2→v3, com o mesmo eval set e oito casos por versão.


> Registro histórico: este piloto Q01 precede a avaliação completa da v1 em Q01-Q08 (run_id `20261023_003912_871419`). Para o comparativo atual, use `pontuacoes_manuais_v1_20261023_003912_871419.csv`.

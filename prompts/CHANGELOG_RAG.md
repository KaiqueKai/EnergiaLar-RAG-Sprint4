# Histórico dos prompts RAG — avaliação concluída

As métricas abaixo vêm das pontuações manuais em `evals/results/`; são fallback manual conforme `evals/manual_rubric.md`, **não são RAGAS**. As médias de resposta consideram os oito casos Q01–Q08; a qualidade de contexto usa sete casos, com Q06=N/A. A pontuação de contexto foi auditada contra os chunks completos presentes nas exportações.

| Versão | Mudança | Modelo | Faithfulness média | Answer relevancy média | Contexto médio | Delta de resposta vs. versão anterior | Estado |
|---|---|---|---:|---:|---:|---:|---|
| v1 | Baseline: grounding, recusa, citações e JSON/Pydantic. | `gemma4:31b` | 0,938 | 0,938 | 0,857 (n=7) | Baseline | Avaliada; run `20261023_003912_871419` |
| v2 | Explicita prompt injection, risco elétrico, escopo e limites de simulação. | `gemma4:31b` | 0,906 | 0,906 | 0,857 (n=7) | -0,031 | Avaliada; matriz `20261021_211148_348705` |
| v3 | Checklist de evidência por afirmação, IDs de fonte, contrato, cobertura do art. 2º estadual e detalhes tarifários com data/unidade/ressalvas. | `gemma4:31b` | 1,000 | 1,000 | 0,857 (n=7) | +0,094 | Recomendada; matriz `20261021_211148_348705` |
| v2 | Mesmo prompt v2, segunda opção de chat para comparação. | `gpt-oss:20b` | 0,594 | 0,594 | 0,857 (n=7) | — | 5/8 saídas estruturadas válidas; três falhas penalizadas com zero no agregado |
| v3 | Prompt v3, segunda opção de chat. | `gpt-oss:20b` | 0,750 | 0,750 | 0,857 (n=7) | +0,156 | 6/8 saídas estruturadas válidas; duas falhas penalizadas com zero no agregado |

## Leitura correta dos resultados

- A passagem v1→v2 **não** melhorou as métricas de resposta: delta -0,031 em faithfulness e answer relevancy.
- A passagem v2→v3 melhorou +0,094 em ambos os critérios para `gemma4:31b`, sem alteração da qualidade média do contexto (+0,000). O resultado sugere melhoria no uso do contexto, não melhoria na recuperação.
- `gemma4:31b` + v3 é a combinação recomendada na amostra: 8/8 saídas estruturadas válidas e citações em 7/7 casos aplicáveis.
- Para `gpt-oss:20b`, as saídas inválidas foram preservadas e receberam zero em faithfulness/relevancy no agregado, como definido na rubrica operacional. Isso mede indisponibilidade da resposta validada, não alegação factual falsa publicada.
- Os contextos completos foram auditados: Q01/Q05/Q07/Q08 receberam 0,75 por chunks adicionais pouco relacionados; Q02/Q03/Q04 receberam 1,00; Q06 é N/A por recusa anterior à recuperação. Essa é uma avaliação manual complementar, não RAGAS.

## Evoluções funcionais

- **v1:** baseline de grounding/citação/recusa com contrato estruturado.
- **v2:** endurece tratamento de contexto não confiável, prompt injection, segurança elétrica e escopo; a média de resposta caiu na amostra testada.
- **v3:** checklist de cobertura e IDs de fontes, atenção a requisitos legais e tarifa, e recuperação suplementar direcionada ao art. 2º. A média Gemma subiu +0,094, sem alteração média do contexto; a alteração observada é de fidelidade/relevância da resposta.

Os resultados são os registrados, não se presumem ganhos a partir do texto do prompt. Para repetir a experiência, use o dataset e os comandos documentados em `INSTRUCOES_TESTE.txt`, salvando novo `run_id` sem sobrescrever resultados anteriores.

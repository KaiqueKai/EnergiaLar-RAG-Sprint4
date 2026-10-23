# Revisão técnica final — EnergiaLar Sprint 4

**Escopo:** auditoria estática do ZIP entregue, consistência de pontuações/contextos, relatórios, README, notebook e proteção de segredos. Não foram realizadas novas chamadas aos modelos. O arquivo original da execução v1 e a matriz com os chunks completos estão incluídos no pacote e foram usados na revisão manual.

## Métricas auditadas

| Indicador | Resultado | Interpretação |
|---|---:|---|
| `gemma4:31b` v1 Faithfulness / relevância | 0,938 / 0,938 | Oito casos; Q04/Q05 com omissões secundárias. |
| `gemma4:31b` v2 | 0,906 / 0,906 | Delta v1→v2 = -0,031 em ambos. |
| `gemma4:31b` v3 | 1,000 / 1,000 | Delta v2→v3 = +0,094 em ambos nesta amostra. |
| Contexto médio auditado (todas as versões/modelos) | 0,857 (n=7; Q06=N/A) | Q01/Q05/Q07/Q08=0,75 por chunks adicionais pouco relacionados; Q02/Q03/Q04=1,00. |
| Citação / estrutura Gemma v3 | 7/7 / 8/8 | Presença mecânica de citação não substitui verificação semântica. |
| GPT-OSS estrutura válida | v2 5/8; v3 6/8 | Cinco falhas JSON/Pydantic ficaram no agregado como zero em F/R, pela rubrica operacional. |

A pontuação do contexto é um fallback manual complementar, não RAGAS. Os mesmos scores de contexto por pergunta foram aplicados a v1/v2/v3 e ambos os modelos porque os chunks nos arquivos de execução são iguais por pergunta. A média 0,857 foi calculada explicitamente a partir das sete perguntas com recuperação.

## Correções desta auditoria

- Atualizadas as pontuações de contexto por pergunta nos CSVs manuais e no CSV da matriz v2/v3; respostas, parâmetros, latências e erros originais permaneceram intactos.
- Sincronizados `resumo_iterations_*.json`, `resumo_models.json`, changelog de prompts, README, relatórios Markdown e o gerador de PDF.
- Corrigida a descrição dos PDFs: o pacote atual inclui manual e lista de compatibilidade GoodWe; o script de download permanece disponível para instalação limpa e atualização de fontes.
- Substituído o estado “pendente” do changelog de prompts pelos resultados medidos já existentes.
- README mantido enxuto, sem checklist de “entregar no Portal”.
- Manifesto SHA-256 regenerado para os arquivos incluídos no pacote. `.env`, `.venv`, `.git`, índice Chroma e saídas de execução brutas não fazem parte do patch.

## Verificação executada nesta auditoria

- `python -m compileall -q src evals tests`: aprovado.
- `pytest`: não pôde ser repetido neste ambiente isolado porque `langchain_core` não está instalado e não houve acesso ao índice de pacotes. O registro já existente no ambiente Windows do projeto informa `48 passed in 4,13 s`; isso não é apresentado como uma execução nova.
- PDF: regerado pelo script do próprio projeto e conferido após renderização visual. Os resultados continuam fallback manual; não houve nova chamada aos modelos.
- Notebook Colab canônico `colab/EnergiaLar_Sprint4_Colab.ipynb` sincronizado com a versão corrigida que contém outputs salvos das verificações Q05/Q06/Q08. A estrutura JSON foi validada nesta auditoria; as saídas são evidência da execução salva, não de uma nova execução feita durante esta revisão. A cópia `EnergiaLar_Sprint4_Colab_CORRIGIDO_JSON.ipynb` foi preservada como referência.

## Limitações que não devem ser escondidas

1. **Embeddings Ollama Cloud:** a tentativa registrada retornou HTTP 401. A issue pública do Ollama sobre embeddings cloud foi aberta em julho de 2026 e continuava aberta na verificação consultada; outra issue oficial informa que, em fevereiro de 2026, não havia modelos de embeddings na Cloud nem roadmap público. Fontes: https://github.com/ollama/ollama/issues/17129 e https://github.com/ollama/ollama/issues/14496. O projeto Windows usa `nomic-embed-text` local; Colab usa Nomic v1.5 em runtime hospedado. Nenhum dos dois deve ser descrito como o endpoint de embeddings Ollama Cloud.
2. **Bônus da rubrica:** o projeto compara dois modelos e duas versões de prompt, conforme a descrição literal “mais de um modelo e mais de um prompt”. Ambos usam Ollama Cloud; se “multi-provider” for interpretado como plataformas/provedores distintos, o ponto fica sujeito à interpretação do professor.
3. **Trabalho em grupo:** a documentação só declara tarefas confirmadas. Não foram inventadas contribuições dos integrantes nem substituídos RMs.
4. **Índice Chroma:** como o código-fonte/base oficial pode mudar, a instalação reproduzível deve reconstruir o índice a partir dos arquivos incluídos/atualizados; não se assume que um índice binário antigo esteja alinhado com todo PDF atual.
5. **Qualidade do contexto:** a média de 0,857 sinaliza ruído de recuperação. Uma mudança para `top_k`, threshold ou reranking exigiria nova avaliação do mesmo dataset antes de ser reivindicada como melhoria, por isso não foi alterado o pipeline medido sem nova evidência.

## Conclusão

Esta auditoria corrige inconsistências verificáveis e deixa as métricas alinhadas entre artefatos. Não é possível prometer nota 100: a limitação literal de embeddings Cloud depende da disponibilidade do serviço e a definição do bônus “multi-provider” pode ser interpretada de mais de uma forma; a rubrica oficial será aplicada pelo professor. A melhor estratégia acadêmica é manter evidência reprodutível e declarações que correspondam ao que foi de fato implementado/testado.

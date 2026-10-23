# Relatório técnico do RAG — Sprint 4

**Projeto:** EnergiaLar | **Disciplina:** Prompt and Artificial Intelligence | **Professor:** Jorge Luiz Gomes

## Pipeline

`PDF/Markdown/TXT/CSV em data/knowledge_base -> PyMuPDFLoader / TextLoader / CSVLoader -> sanitização de padrões conhecidos de injection -> RecursiveCharacterTextSplitter -> nomic-embed-text via Ollama local -> ChromaDB persistente -> retriever -> prompt RAG versionado -> gemma4:31b no Ollama Cloud -> JSON validado por ConsultaRecarga (Pydantic v2) -> citações e interface Streamlit`.

## Base de conhecimento e rastreabilidade

O pacote analisado inclui os binários do manual oficial HCA G2 em inglês e da lista oficial GoodWe de compatibilidade de carregadores/inversores (fonte complementar). O manual é obrigatório para liberar a indexação. No workspace Windows usado nesta validação, os dois PDFs foram baixados e o build do Chroma reportou 174 chunks. Em uma instalação limpa ou após atualização dos documentos, execute `scripts/baixar_manual_oficial.ps1` para baixar/validar os PDFs e reconstrua o índice; não substitua arquivos oficiais por conteúdo sintético. O pacote já contém um resumo técnico Markdown ligado a páginas primárias, FAQ do EnergiaLar, protocolo condominial orientativo, resumo das leis paulistas com links integrais, tabela de preços simulados, tabela CSV/Markdown dos componentes tarifários oficiais Enel SP (vigência indicada desde 04/07/2026, classe B1/modalidades especificadas) e perguntas de validação. Os valores da Enel não são o total da fatura e não se aplicam automaticamente a unidades de outras distribuidoras. O script `scripts/baixar_manual_oficial.ps1` valida PDFs antes de os salvar (pode ser invocado por `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\baixar_manual_oficial.ps1` sem alterar a política permanente do Windows); o manual é obrigatório para o gate de indexação, e a lista de compatibilidade é fonte oficial complementar. URLs primárias: `https://br.goodwe.com/download-hca-g2-series`, `https://br.goodwe.com/Api/downloadFile?id=2496&mid=60&type=2`, `https://br.goodwe.com/Api/downloadFile?id=4535&mid=60&type=2`. Não confundir os resumos da equipe com documentos oficiais.

Fonte da folha de dados oficial: `https://br.goodwe.com/Api/downloadFile?id=3931&mid=60&type=1`. Página da linha HCA G2: `https://br.goodwe.com/download-hca-g2-series`. A tarifa real não é fixa neste arquivo: a tabela tem apenas dois valores didáticos, claramente marcados como simulados, e remete o usuário à fatura/distribuidora para valor efetivo.

## Chunking e recuperação

- `chunk_size=800`, `chunk_overlap=120`, separadores orientados a títulos/parágrafos.
- `top_k=8` e `min_relevance_score=0.15` como configuração atual; calibrar com o eval set, pois o limiar não é garantia universal. Em perguntas jurídicas sobre condomínio/recarga, há uma busca complementar dirigida ao trecho do art. 2º da Lei Estadual SP nº 18.403/2026; o trecho só é anexado após validação textual de artigo, capacidade mínima e instalação futura.
- O Chroma mantém persistência em `storage/chroma/`; mudança de conteúdo, modelo de embeddings ou parâmetros invalida o índice pela metadata.
- Chunks da mesma página compartilham ID de citação; documentos textuais são citados por nome, sem paginação.

## Grounding e segurança

O prompt v2 trata o contexto recuperado como dado não confiável, exige resposta ancorada nas fontes, recusa quando faltar evidência, impede recomendações específicas de dimensionamento elétrico e diferencia valores didáticos de tarifas oficiais. O loader remove linhas que correspondem a padrões heurísticos conhecidos de prompt injection; o filtro de saída detecta alguns padrões de credencial. Esses guardrails reduzem riscos, mas não são uma garantia formal. Q06-Q08 e `tests/test_security.py` cobrem casos conhecidos.

## Avaliação

`evals/dataset.json` tem oito casos, incluindo perguntas suportadas, fora de escopo, segurança elétrica e prompt injection. `evals/manual_rubric.md` documenta uma rubrica de 0 a 1 para `faithfulness` e `answer_relevancy`, fallback aceito pelo enunciado caso RAGAS não seja suportado, mais uma nota complementar para qualidade do contexto recuperado. O CSV também registra presença automática de citação. Os CSVs por rodada preservam o `run_id`, prompt, modelo, parâmetros, latência, fontes, erro e notas manuais. Q04 foi corrigida e validada em consulta real após a busca complementar. A matriz `20261021_211148_348705` foi revisada manualmente: Gemma v2 faithfulness/relevância=0,906/0,906; Gemma v3=1,000/1,000; GPT-OSS v2=0,594/0,594; GPT-OSS v3=0,750/0,750. Após auditoria manual dos chunks completos, a qualidade média do contexto ficou 0,857 nos sete casos aplicáveis e N/A para Q06 (recusa antes de recuperar). São scores manuais de fallback, não RAGAS. O GPT-OSS teve cinco saídas JSON inválidas que receberam zero nas métricas da resposta pelo contrato operacional; falhas preservadas nos CSVs.

## Compatibilidade de embeddings Cloud

O teste real retornou `401 Unauthorized` ao solicitar embeddings em `https://ollama.com`. A documentação e o mantenedor do Ollama indicam que embeddings Cloud não estão disponíveis. Para fazer o RAG funcionar, o pacote configura `EMBEDDING_HOST=http://localhost:11434` mantendo `nomic-embed-text`; o chat permanece na nuvem. Essa alternativa diverge do trecho literal `Ollama Cloud` do PDF e não é apresentada como conformidade plena. Evidências e instruções: `docs/COMPATIBILIDADE_EMBEDDINGS_CLOUD.md`.


## Pontuação do baseline v1

A avaliação manual completa da v1 (`20261023_003912_871419`) abrange Q01-Q08 com `gemma4:31b`: contexto médio auditado 0,857 em sete casos aplicáveis (Q06=N/A), faithfulness 0,938, answer relevancy 0,938, citações 7/7 e JSON válido 8/8. V1 ficou em 0,938 e v2 em 0,906 (delta v1→v2 = -0,031); v2→v3 melhorou +0,094 nos dois critérios de resposta. A nota de contexto da v1 foi auditada contra os trechos integrais presentes em `evals/results/revisao_assistente_20261023_003912_871419.md`. Q01/Q05/Q07/Q08 receberam 0,75 por ruído de recuperação; Q02/Q03/Q04 receberam 1,00.

## Versão Colab e limite cloud

A alternativa `colab/EnergiaLar_Sprint4_Colab.ipynb` executa `nomic-ai/nomic-embed-text-v1.5` no runtime hospedado do Google Colab e o chat em `gemma4:31b` pelo Ollama Cloud. O modelo usa os prefixos Nomic `search_document:` e `search_query:`. Não é o endpoint gerenciado de embeddings do Ollama Cloud; essa diferença permanece registrada em `docs/COMPATIBILIDADE_EMBEDDINGS_CLOUD.md`.

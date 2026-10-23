# Evolução da Sprint 3 para a Sprint 4 — EnergiaLar

## Origem correta e estratégia de integração

Este pacote é um **projeto integrado de trabalho**: preserva os módulos conversacionais examinados da Sprint 3 do projeto EnergiaLar do professor Jorge (`https://github.com/KaiqueKai/EnergiaLar`) e acrescenta módulos RAG independentes. Não usa ChargeGrid Intelligence/Lucas como base. O diretório `docs/sprint3_local_snapshot/` guarda materiais históricos disponíveis para comparação; os módulos ativos da Sprint 3 ficam na raiz do projeto.

A camada conversacional herdada permanece em `src/chatbot.py`, `src/chain/`, `src/guardrails/`, `src/schemas/`, prompts de sistema e scripts de avaliação conversacional. A Sprint 4 acrescenta `src/rag/`, `app/`, documentos da base e scripts/relatórios de avaliação RAG. Não é necessário aplicar outra sobreposição a esta pasta.

## Antes: Sprint 3

A Sprint 3 examinada é um assistente conversacional para perguntas relacionadas à recarga de veículos elétricos e eficiência energética. Usa LCEL/LangChain, prompt externo, histórico por sessão e contrato de resposta validado por Pydantic v2. Os scripts antigos comparam baseline/modelos e validade da resposta. O comparativo conversacional não registra pipeline RAG com ChromaDB persistente nem citações por trecho/página.

A referência histórica publicada dos cinco casos happy-path comparáveis registra 192,6 tokens médios, 9,356 s de latência média e saída estruturada válida em 5/5 casos; isso descreve execução/forma, **não uma nota subjetiva de qualidade**. Os scores qualitativos históricos não foram fabricados.

## Depois: Sprint 4

Acrescenta loaders `PyMuPDFLoader`/`TextLoader`/`CSVLoader`, `RecursiveCharacterTextSplitter` (800 caracteres e overlap 120), `nomic-embed-text`, ChromaDB persistente, recuperação semântica com limiar configurável, prompts RAG `v1`, `v2` e `v3`, citações documento/página, guardrails heurísticos, interface Streamlit e avaliação com rubrica manual para `faithfulness` e `answer_relevancy`. A avaliação também registra qualidade manual do contexto recuperado e presença automática de citações.

O pacote atual inclui os binários do manual original GoodWe HCA G2 e da lista oficial de compatibilidade; instalações limpas ou atualizações devem validá-los pelo script oficial. No workspace Windows testado, ambos foram baixados e o build real do índice informou 174 chunks. O índice bloqueia a construção sem o manual obrigatório. A base contém também uma folha de dados claramente identificada como resumo acadêmico, FAQ, protocolo condominial não normativo, referências primárias às leis paulistas, preço didático simulado e componentes tarifários oficiais publicados pela Enel SP (com validade/jurisdição registradas). O resumo da equipe não substitui o documento oficial do fabricante nem a tarifa de uma distribuidora é apresentada como valor universal.

## Correção de recuperação legal verificada em 21/10/2026

A pergunta Q04 sobre as Leis Estadual SP nº 18.403/2026 e Municipal nº 17.336/2020 omitia o art. 2º porque o top-k semântico original selecionava trechos mais relacionados ao art. 1º, à lei municipal e ao protocolo. A solução adiciona uma busca complementar dirigida ao artigo e uma regra em `rag_v3.md` que exige mencionar a capacidade mínima quando a evidência estiver no contexto. Na consulta real posterior à correção, a resposta citou a previsão de capacidade mínima para futuras estações, apresentou três fontes e validou o schema Pydantic. A suíte automatizada no Windows passou com 48 testes.

## Problemas encontrados e soluções

1. **Sprint 3 sem busca vetorial:** mantida a cadeia conversacional original e acrescentada uma camada RAG desacoplada.
2. **Embeddings Cloud indisponíveis:** o teste real da conta retornou `401 Unauthorized` para `nomic-embed-text` em `https://ollama.com`; a documentação pública descreve Cloud chat e embeddings locais. Para que o RAG seja executável, mantém-se `gemma4:31b` no chat Cloud e usa-se o mesmo modelo `nomic-embed-text` em Ollama local para indexação e consulta. Isso é um desvio explícito do requisito literal `Ollama Cloud` para embeddings, não conformidade integral.
3. **Risco de alucinação/citação falsa:** prompts versionados, recusa por falta de contexto, IDs de fonte derivados dos metadados recuperados, validação Pydantic e testes de guardrails; o filtro de injection é heurístico e não garantia absoluta.
4. **Confusão entre valor simulado e tarifa real:** os cenários didáticos foram mantidos marcados como simulados; uma tabela oficial Enel SP foi acrescentada separadamente com data, classe, modalidade e fonte.
5. **Histórico de métricas suscetível a mistura:** CSVs exclusivos por execução, `run_id`, parâmetros, erros, latência, contexto recuperado, três notas manuais e presença de citação; comparação entre versões só no mesmo run/dataset.

## Comparativo antes/depois

| Indicador | Sprints 1/2 (versão original; dados disponíveis limitados) | Sprint 4 |
|---|---|---|
| Arquitetura | Assistente conversacional LCEL, memória por sessão, guardrails e schema Pydantic v2; sem RAG vetorial na versão examinada. | Camada RAG independente, Chroma persistente, Streamlit e fontes visíveis, mantendo a Sprint 3. |
| Busca/contexto | Busca vetorial e contexto recuperado não medidos no baseline. | Chunks 800/120, `top_k=8`, limiar inicial 0,15; contexto médio auditado 0,857 em sete casos recuperáveis (Q06=N/A), fallback manual. |
| Citações | Não registradas no comparativo conversacional original por documento/página. | Fonte/página exibida e presença de citação registrada em cada resposta aplicável. |
| `faithfulness` e `answer_relevancy` | N/A: a avaliação original não era RAG. | v1 (8 casos): Gemma 0,938/0,938; v2 0,906/0,906; v3 1,000/1,000. GPT-OSS: v2 0,594/0,594 e v3 0,750/0,750. Fallback manual, não RAGAS. |
| Iterações e modelos | O baseline histórico é preservado, sem tratá-lo como score RAG. | Duas iterações comparáveis v2/v3 com ganho registrado; Gemma 8/8 JSON válidos e GPT-OSS 5/8 em v2, 6/8 em v3. Cinco falhas JSON do segundo modelo estão preservadas. |

## Limitações ainda em aberto antes do envio

- O link do novo repositório público da Sprint 4 precisa ser preenchido no TXT e no README depois que o grupo criar/publicar o repositório. Confirmar no Portal o código exato da turma.
- A implementação técnica e a avaliação desta versão foram executadas por Kaique. As revisões propostas aos colegas permanecem pendentes; não são descritas como tarefas concluídas.
- A versão principal de Windows usa `nomic-embed-text` local porque o endpoint de embeddings Ollama Cloud retornou 401. O Colab complementar executa Nomic Embed Text v1.5 na VM remota do Colab e mantém o chat via Ollama Cloud. Esta é uma alternativa cloud, mas não um endpoint gerenciado de embeddings do Ollama Cloud; a conformidade literal precisa ser confirmada com o professor caso o provedor seja obrigatório.
- O pacote atual inclui os PDFs binários oficiais GoodWe. Em instalação limpa ou após atualizar os documentos, execute `scripts/baixar_manual_oficial.ps1` e reconstrua ChromaDB antes de avaliar. O registro do workspace Windows reportou 174 chunks.
- O notebook Colab foi verificado estaticamente, mas a primeira execução live ainda precisa ser feita em uma sessão Google Colab autenticada com a chave Ollama Cloud.

## Equipe e divisão de trabalho

| Integrante | RM | Registro desta versão |
|---|---:|---|
| Kaique Da Silva Assis | 572718 | Implementação RAG, correções Q04/Q05, prompts v1/v2/v3, testes, avaliação manual e documentação (concluído conforme relato do responsável). |
| Andre Debiazzi Baldi Negrini | 569062 | Revisão sugerida de guardrails e prompt injection — pendente; não contabilizada como concluída. |
| Vinicius Cristal de Oliveira | 572049 | Revisão sugerida da interface e citações — pendente; não contabilizada como concluída. |
| Lucas Barros | 571528 | Revisão sugerida da matriz de modelos e parâmetros — pendente; não contabilizada como concluída. |
| Renan Eskildssen | 571097 | Revisão sugerida de fontes e checklist de entrega — pendente; não contabilizada como concluída. |

## Versão complementar Colab

`colab/EnergiaLar_Sprint4_Colab.ipynb` cria a base e o índice Chroma na sessão remota do Colab com `nomic-ai/nomic-embed-text-v1.5` e usa `gemma4:31b` por Ollama Cloud para respostas. O prefixo `search_document:` é usado para os chunks e `search_query:` para perguntas. Essa configuração não instala embeddings no PC local, porém não equivale à API de embeddings hospedados pelo Ollama Cloud; consultar `docs/COMPATIBILIDADE_EMBEDDINGS_CLOUD.md`.

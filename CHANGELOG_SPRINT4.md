> **Leitura do histórico:** entradas anteriores registram o estado na data em que foram escritas. A seção final desta revisão consolida os artefatos e métricas válidos para o pacote atual; status antigos de “pendente” não descrevem o estado final.

# Changelog — EnergiaLar Sprint 4 (Jorge)

## Continuidade correta
- Pacote único e integrado, usando como base o EnergiaLar da Sprint 3 do professor Jorge: `https://github.com/KaiqueKai/EnergiaLar`.
- Mantidos os módulos conversacionais herdados na raiz do projeto: `src/chatbot.py`, `src/chain/`, `src/guardrails/`, `src/schemas/`, prompts conversacionais e evaluadores antigos.
- `docs/sprint3_local_snapshot/` preserva os materiais históricos disponíveis. Não foi usado o projeto ChargeGrid/Lucas.

## Implementação Sprint 4
- Loaders `PyMuPDFLoader`, `TextLoader` e `CSVLoader`.
- Chunking inicial `RecursiveCharacterTextSplitter` de 800 caracteres / overlap 120.
- `nomic-embed-text`, ChromaDB persistente, hash da base/configuração e reindexação controlada.
- Pipeline de recuperação -> prompt RAG versionado `v1/v2/v3` -> chat Cloud `gemma4:31b` -> JSON validado pelo schema Pydantic v2 herdado.
- Interface Streamlit com fontes/citações visíveis.
- Guardrails heurísticos para prompt injection/saída que pareça credencial, recusa fora de escopo e validação de saída; são camadas defensivas, não prova formal de segurança.
- Avaliação com rubrica manual autorizada pelo enunciado: `faithfulness`, `answer_relevancy` e qualidade do contexto recuperado, além de presença automática de citações. CSV por execução preserva run_id, parâmetros, latência, contextos, fontes, erros, scores e a pergunta/eventos de segurança após o filtro de injection. Foi adicionada a matriz opcional modelo × prompts para a parcela bônus, mantendo-a separada das avaliações mínimas.

## Expansão e rastreabilidade da base
- Script `scripts/baixar_manual_oficial.ps1` baixa o manual original GoodWe HCA G2 (obrigatório para indexação) e tenta baixar a lista oficial de compatibilidade da GoodWe. Os arquivos não puderam ser baixados para o pacote neste ambiente; precisam ser baixados e validados no Windows e não são substituídos por documentos sintéticos.
- Adicionadas referências primárias à Lei Estadual SP 18.403/2026 e Lei Municipal SP 17.336/2020, com escopos e limites de aplicação indicados.
- Adicionada tabela oficial de componentes tarifários Enel SP, vigente segundo o site a partir de 04/07/2026, separada dos preços simulados. Não é uma tarifa universal nem o total da fatura.
- Um documento resumido acadêmico continua identificado como resumo e nunca como manual oficial.

## Modelos
- Modelo principal preservado: `gemma4:31b` no Ollama Cloud (chat testado com sucesso pelo usuário).
- `gpt-oss:20b` foi confirmado acessível pelo teste curto da conta e entrou na matriz real v2/v3. A matriz teve cinco saídas JSON inválidas em 16 chamadas desse modelo; esse resultado e a recomendação de manter `gemma4:31b` como principal estão documentados.
- `nomic-embed-text` no Ollama Cloud retornou `401 Unauthorized`; documentação pública atual não apresenta endpoint público Cloud de embeddings. Para deixar o RAG funcional, a configuração de execução usa `nomic-embed-text` via Ollama local e mantém o chat Cloud. Esse desvio literal está documentado.

## Validação e honestidade dos resultados
- A sintaxe da árvore final foi conferida com `compileall` na etapa de empacotamento.
- No workspace Windows do usuário, depois das correções de Q04/Q05, `pytest -q` terminou com **48 passed in 1.24s**.
- A consulta real Q04 em `v3` incluiu art. 1º e art. 2º da Lei Estadual SP nº 18.403/2026, com três fontes, relevância `0.8741` e contrato Pydantic válido.
- A consulta Q05 foi previamente verificada com os componentes TUSD e TE-BVD, unidade, vigência e ressalva sobre total da fatura. Q01, Q03 e os casos de segurança Q06-Q08 também tiveram verificação manual no Streamlit.
- Os PDFs oficiais GoodWe e o índice com 174 chunks estavam presentes no workspace Windows testado, mas os binários não estão dentro deste ZIP. Uma instalação limpa deve baixar os PDFs e reconstruir o índice.
- `nomic-embed-text` em Ollama Cloud retornou `401 Unauthorized`; os embeddings locais funcionaram e o chat Cloud respondeu `EnergiaLar OK`. O desvio literal do requisito Cloud continua declarado.
- Os scores de qualidade para a comparação v2/v3 e a comparação de dois modelos ainda estão pendentes. Nenhum score de avaliação RAG foi fabricado.

## Correções após validação real de Q04/Q05 — 21/10/2026
- Recuperador RAG atualizado para executar uma busca complementar dirigida ao art. 2º da Lei Estadual SP nº 18.403/2026 em perguntas jurídicas de condomínio/recarga, validando os termos artigo, capacidade mínima e instalação futura antes de adicionar o trecho.
- Prompt `rag_v3.md` reforçado para exigir separação entre as duas leis paulistas, cobertura do art. 2º quando a evidência estiver no contexto, detalhes da tabela Enel e citação específica por afirmação, sem inventar números.
- Incluídos testes de regressão para a busca complementar e os requisitos do prompt v3. A suíte Windows do projeto ativo apresentou 48 testes aprovados; uma chamada real Q04 em v3 citou o art. 2º (relevância 0,8741, três fontes, Pydantic válido).
- `TOP_K` padrão e `.env.example` alinhados em 8 para reproduzir a recuperação verificada em Q05.
- A comparação v2 × v3 e os scores de `faithfulness`, `answer_relevancy` e qualidade do contexto continuam pendentes; não foram fabricados.


## Correção de consistência do pacote — 21/10/2026
- A versão de distribuição agora mantém o item Q04 esperado para o art. 2º e a regra do prompt v3 que explicita a vigência tarifária de 04/07/2026 somente quando confirmada pela fonte recuperada.
- Adicionado `tests/test_prompt_v3_domain_rules.py` para impedir regressões nesses dois requisitos.
- O script de atualização valida esses requisitos antes de copiar arquivos para o projeto; um pacote inconsistente é recusado antes de tocar na pasta existente.


## Avaliação comparativa final - 20261021_211148_348705
- Reavaliadas 32 saídas: dois modelos (`gemma4:31b`, `gpt-oss:20b`) por dois prompts (v2/v3), os mesmos oito casos Q01-Q08.
- Scores manuais pela rubrica: gemma v2 faithfulness/relevancy 0,906/0,906; gemma v3 1,000/1,000. GPT-OSS v2 0,594/0,594; GPT-OSS v3 0,750/0,750. Qualidade de contexto: 1,000 em sete casos aplicáveis; Q06 N/A.
- Cinco saídas JSON/Pydantic inválidas do GPT-OSS foram registradas (v2 Q01/Q03/Q04; v3 Q04/Q05); para o agregado foi aplicada penalização operacional 0,00 nas dimensões de resposta porque a aplicação reteve a saída. Não se chama isso de RAGAS.
- Recomendação: `gemma4:31b` + prompt v3, com 8/8 respostas estruturadas válidas, citações em 7/7 casos aplicáveis e melhoria manual medida versus v2.
- Relatório PDF e documentação foram atualizados. Mantidas a limitação de embeddings local (Cloud retornou 401) e a necessidade de confirmar contribuições/turma/repositório antes da submissão.


## Fechamento documental complementar

- Incluído `ENTREGA_SPRINT4.txt` com os cinco nomes/RMs, turma de referência e campo para URL do repositório Sprint 4.
- Incluído `colab/EnergiaLar_Sprint4_Colab.ipynb` e seu pacote de fontes. Nomic Embed Text v1.5 roda no runtime cloud do Colab; o notebook usa o Ollama Cloud para chat e explicita a diferença frente ao endpoint cloud de embeddings indisponível.
- O relatório registra v1/Q01 como piloto n=1 (score 1.000, sem generalizar para oito casos) e mantém o delta v2→v3 baseado na matriz completa.
- A divisão de tarefas deixa explícito que a implementação técnica confirmada foi feita por Kaique; as revisões sugeridas aos demais estão pendentes e não são declaradas como concluídas.


## Pontuação completa da v1 — 23/10/2026
- Pontuadas manualmente as oito respostas Q01-Q08 do run_id `20261023_003912_871419` (modelo `gemma4:31b`), sem novas chamadas de avaliação.
- Revisão final v1: Q07 foi reavaliada diretamente pela rubrica (1,00/1,00); médias recalculadas para faithfulness 0,938 e answer relevancy 0,938; v1→v2 = -0,031 e v2→v3 = +0,094. Contexto v1 permanece provisório até auditoria dos trechos integrais.
- Nota de evolução corrigida: v1→v2 = -0,031; v2→v3 = +0,094 nas duas métricas de resposta. O delta 0,000 da revisão inicial foi supersedido após a correção rubricada da Q07.
- Adicionados `evals/results/pontuacoes_manuais_v1_20261023_003912_871419.csv`, revisão itemizada e resumo JSON. PDF de evolução regenerado.
- Nota de transparência: o log usado para esta atualização contém as respostas e nomes das fontes, mas o Markdown local com trechos integrais de contexto não estava no pacote analisado; os scores de contexto da v1 ficam provisórios até essa conferência.


## Revisão final de consistência (23/10/2026)

- Corrigida a nota manual de Q07 da v1 para 1,00 em faithfulness e answer relevancy, conforme a rubrica publicada.
- Recalculada a média da v1 para 0,938; v1→v2 = -0,031 e v2→v3 = +0,094.
- README reduzido e checklists operacionais de submissão removidos.
- Notebook Colab atualizado para a versão corrigida com resposta textual, citações e validação Pydantic local.
- `.gitignore` ampliado para segredos e arquivos de chave comuns.
- Limites de embeddings Cloud, bônus multi-provider, score de contexto v1 e verificação de divisão de trabalho continuam explícitos.


## Estado consolidado após auditoria final (23/10/2026)

- Auditoria manual dos chunks completos v1/v2/v3 concluída: contexto médio 0,857 em sete casos recuperáveis (Q06=N/A), com notas por pergunta preservadas em `evals/results/pontuacoes_manuais_v1_20261023_003912_871419.csv` e na matriz v2/v3. Não foi executada nova chamada de modelo.
- Médias de resposta Gemma: v1 0,938; v2 0,906; v3 1,000. Delta v1→v2 -0,031; v2→v3 +0,094. A melhoria ocorre na resposta, não na nota média de contexto.
- Os dois PDFs oficiais GoodWe estão presentes em `data/knowledge_base/` no pacote entregue; scripts de download continuam disponíveis para instalações limpas/atualizações.
- O notebook canônico `colab/EnergiaLar_Sprint4_Colab.ipynb` foi sincronizado com a versão corrigida com outputs salvos de Q05/Q06/Q08; a cópia `EnergiaLar_Sprint4_Colab_CORRIGIDO_JSON.ipynb` foi preservada. Os outputs documentam a execução salva, sem alegar nova execução nesta auditoria.
- Limitações sem solução documentada permanecem declaradas: embeddings no endpoint Ollama Cloud não estavam disponíveis na verificação pública; ambos os modelos comparados usam Ollama Cloud, embora a rubrica literalmente descreva o bônus como mais de um modelo e mais de um prompt; contribuições individuais devem refletir tarefas realmente realizadas. O teste completo de contexto identifica média 0,857 em sete casos recuperáveis; os contextos Q01/Q05/Q07/Q08 têm ruído adicional.

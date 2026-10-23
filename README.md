# EnergiaLar — Assistente documental RAG

**FIAP × GoodWe Brasil · Prompt and Artificial Intelligence · 2º semestre de 2026 · Prof. Jorge Luiz Gomes**

O EnergiaLar evolui o projeto conversacional da Sprint 3 para um assistente documental com recuperação aumentada por geração (RAG). A versão preserva a camada LCEL/Pydantic v2 e adiciona uma base indexada, citações de fontes, avaliação por rubrica manual e interface Streamlit.

## Funcionalidades

- Pipeline de documentos PDF, Markdown, TXT e CSV com `RecursiveCharacterTextSplitter`, embeddings e ChromaDB persistente.
- Recuperação semântica com filtro de relevância e busca suplementar direcionada para evidência legal crítica do art. 2º estadual.
- Prompts RAG versionados (`v1`, `v2`, `v3`) com grounding, citações e recusa quando a base não sustenta a resposta.
- Validação da resposta estruturada com Pydantic v2 e bloqueios heurísticos para padrões de prompt injection e possíveis credenciais.
- Interface web em Streamlit, com fontes, páginas de PDF e trechos recuperados.
- Avaliação de dois modelos e duas versões de prompt, além de avaliação separada do baseline v1.

## Arquitetura

```text
PDF / Markdown / TXT / CSV
          ↓
Loaders + sanitização heurística
          ↓
Chunking (800 caracteres; overlap 120)
          ↓
Embeddings → ChromaDB persistente
          ↓
Retriever (top-k=8; limiar inicial=0,15)
          ↓
Prompt RAG versionado → Ollama Cloud (chat)
          ↓
Validação Pydantic v2 → resposta + fontes na interface
```

A recuperação jurídica possui uma busca complementar direcionada para não perder o trecho sobre capacidade mínima futura quando a pergunta envolve as regras legais de recarga em condomínios. A configuração é um ponto inicial calibrado com o conjunto de avaliação, não uma garantia universal de recuperação.

## Requisitos e execução (Windows / PowerShell)

Use Python 3.13 e execute os comandos na raiz do projeto:

```powershell
py -3.13 -m venv .venv
$py = ".\.venv\Scripts\python.exe"
& $py -m pip install --upgrade pip
& $py -m pip install -r requirements-dev.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Configure `OLLAMA_API_KEY` no `.env`. Não compartilhe esse arquivo. O projeto principal usa `gemma4:31b` no Ollama Cloud para chat e `nomic-embed-text` no Ollama local para embeddings. Para preparar a base e executar a interface:

```powershell
ollama pull nomic-embed-text
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\baixar_manual_oficial.ps1
& $py -m src.rag.check_setup
& $py -m src.rag.build_index --force
& $py -m streamlit run app/streamlit_app.py
```

O pacote analisado inclui `00_manual_oficial_goodwe_hca_g2_en.pdf` e `00b_compatibilidade_goodwe_ev_hca_g2_en.pdf` em `data/knowledge_base/`. O manual oficial é obrigatório para liberar a indexação; a lista de compatibilidade é fonte complementar. Em uma instalação limpa ou após a atualização do fabricante, `scripts/baixar_manual_oficial.ps1` baixa e valida os PDFs antes de reconstruir o índice.

## Testes

```powershell
& $py -m compileall -q src evals app scripts tests
& $py -m pytest -q
```

Os testes automatizados são offline: validam contratos, configuração, sanitização, recuperação, citações e guardrails; não substituem a verificação real de credenciais, disponibilidade dos modelos, downloads oficiais ou construção do índice em uma instalação limpa. O registro de execução do projeto Windows informa `48 passed` em 4,13 s; consulte `docs/STATUS_VALIDACAO.md` para saber o alcance e as limitações dessa evidência.

## Avaliação registrada

As médias são **fallback manual documentado**, não RAGAS. A rubrica está em `evals/manual_rubric.md`; cada média de resposta usa os oito casos Q01–Q08 e penaliza saída estruturada inválida com zero no agregado, conforme a regra operacional publicada.

| Modelo | Prompt | Faithfulness | Answer relevancy | Estrutura válida | Latência média |
|---|---|---:|---:|---:|---:|
| `gemma4:31b` | v1 | 0,938 | 0,938 | 8/8 | Não registrada |
| `gemma4:31b` | v2 | 0,906 | 0,906 | 8/8 | 3,878 s |
| `gemma4:31b` | v3 | 1,000 | 1,000 | 8/8 | 3,781 s |
| `gpt-oss:20b` | v2 | 0,594 | 0,594 | 5/8 | 7,403 s |
| `gpt-oss:20b` | v3 | 0,750 | 0,750 | 6/8 | 6,920 s |

A auditoria dos contextos completos está em `evals/results/revisao_assistente_20261023_003912_871419.md` e foi aplicada às avaliações v1/v2/v3. Contexto médio = **0,857 em sete casos** (Q06=N/A); Q01, Q05, Q07 e Q08 receberam 0,75 por chunks adicionais pouco relacionados. Em resposta, v1=0,938, v2=0,906 e v3=1,000 para Gemma: v1→v2 caiu 0,031; v2→v3 melhorou 0,094. Em `gpt-oss:20b`, cinco saídas JSON/Pydantic inválidas foram preservadas e penalizadas na média conforme a regra operacional.

Parâmetros da matriz v2/v3: `temperature=0`, `top_p=0.9`, `max_tokens=600`, `top_k=8`, `min_relevance_score=0.15`, `chunk_size=800`, `chunk_overlap=120`. A amostra comparativa mantém o mesmo conjunto de oito perguntas por versão.

## Limitações e interpretação

- **Embeddings no Ollama Cloud:** a chamada testada retornou `401 Unauthorized`. A documentação atual do Ollama e o issue público de julho de 2026 descrevem a limitação do endpoint Cloud para embeddings. Por isso, a versão principal usa embeddings locais e mantém chat no Cloud; isto não satisfaz literalmente o requisito de embeddings hospedados no Ollama Cloud. Ver `docs/COMPATIBILIDADE_EMBEDDINGS_CLOUD.md`.
- **Alternativa Colab:** `colab/EnergiaLar_Sprint4_Colab.ipynb` executa Nomic Embed Text no runtime do Colab e usa Ollama Cloud para chat. É uma alternativa hospedada, mas não é o endpoint de embeddings do Ollama Cloud.
- **Bônus da rubrica:** o projeto compara dois modelos (`gemma4:31b` e `gpt-oss:20b`) e dois prompts (v2/v3), cumprindo literalmente a descrição “mais de um modelo e mais de um prompt”. Como ambos usam Ollama Cloud, o ponto depende de como o professor interpreta o termo “multi-provider” (provedores distintos versus modelos/prompts distintos).
- **Segurança:** sanitização de documentos, detecção de injection e bloqueio de possíveis credenciais são heurísticos; não substituem auditoria de segurança nem garantem bloqueio de todo ataque.
- **Operação real:** o protótipo não controla nem telemetria um carregador GoodWe físico. O protocolo de condomínio é orientativo, não norma legal; valores da tabela didática são simulados e separados dos dados publicados da Enel SP.
- **Equipe:** integrantes e RMs estão listados abaixo. A documentação registra somente as contribuições verificáveis nesta versão; não atribui tarefas como concluídas sem evidência.

## Equipe

| Integrante | RM |
|---|---:|
| Kaique Da Silva Assis | 572718 |
| Andre Debiazzi Baldi Negrini | 569062 |
| Vinicius Cristal de Oliveira | 572049 |
| Lucas Barros | 571528 |
| Renan Eskildssen | 571097 |

## Documentação e organização

- `docs/arquitetura_sprint4.md` — arquitetura e fluxo da aplicação.
- `docs/relatorio_rag.md` — pipeline, recuperação, grounding e limites.
- `docs/relatorio_modelos.md` — parâmetros, comparações e justificativas de pontuação.
- `docs/relatorio_evolucao_sprint4.pdf` — relatório de evolução com tabela antes/depois.
- `docs/REVISAO_FONTES_EXTERNAS.md` — fontes oficiais e limites de interpretação.
- `docs/COMPATIBILIDADE_EMBEDDINGS_CLOUD.md` — evidências do limite de embeddings.
- `docs/STATUS_VALIDACAO.md` — estado técnico conhecido e alcance das verificações.
- `evals/results/` — resultados por execução, CSVs pontuados e resumo JSON.
- `prompts/` — prompts versionados e histórico de alterações.
- `tests/` — testes automatizados.

## Fontes primárias

- [GoodWe Brasil — série HCA G2](https://br.goodwe.com/carregadores-hca-g2-goodwe)
- [Manual oficial GoodWe HCA G2](https://br.goodwe.com/Api/downloadFile?id=2496&mid=60&type=2)
- [Lei Estadual SP nº 18.403/2026](https://al.sp.gov.br/repositorio/legislacao/lei/2026/lei-18403-18.02.2026.html)
- [Lei Municipal SP nº 17.336/2020](https://legislacao.prefeitura.sp.gov.br/lei-17336-de-30-de-marco-de-2020)
- [Enel SP — tarifas de energia](https://www.enel.com.br/pt-saopaulo/Para_Voce/tarifa-energia-eletrica.html)
- [Ollama — embeddings](https://docs.ollama.com/capabilities/embeddings)
- [Ollama — discussão sobre embeddings no Cloud](https://github.com/ollama/ollama/issues/17129)

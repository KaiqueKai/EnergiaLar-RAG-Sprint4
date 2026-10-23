# Arquitetura RAG - Sprint 4 (EnergiaLar)

## Continuidade da Sprint 3 (Jorge)

O projeto original permanece disponível: `src/chatbot.py` preserva a cadeia LCEL, memória por sessão, `ConsultaRecarga` em Pydantic v2, os prompts conversacionais e os scripts de avaliação anteriores. O RAG foi acrescentado como módulo separado para que a cadeia original possa continuar sendo executada e comparada.

## Fluxo RAG da Sprint 4

```text
PDF/Markdown/TXT/CSV na allowlist data/knowledge_base
        ↓
PyMuPDFLoader / TextLoader / CSVLoader
        ↓
Sanitização de padrões conhecidos de prompt injection
        ↓
RecursiveCharacterTextSplitter (800 / 120)
        ↓
OllamaEmbeddings (nomic-embed-text, endpoint local; desvio literal Cloud documentado)
        ↓
ChromaDB persistente + metadados de versão/hash
        ↓
Busca semântica top-k + limiar de relevância
        ↓
Prompt RAG v1/v2/v3 (SystemMessage separado da pergunta/contexto)
        ↓
Ollama Cloud / ChatOllama
        ↓
JSON parseado e validado por ConsultaRecarga (Pydantic v2)
        ↓
Referências de fonte + Streamlit
```

## Decisões

- `src/rag/loader.py`: apenas arquivos sob a pasta autorizada de conhecimento entram no índice; o manual oficial deve ser obtido com `scripts/baixar_manual_oficial.ps1`.
- `src/rag/chunking.py`: splitter hierárquico com 800 caracteres e overlap de 120; os mesmos parâmetros ficam fixos na comparação de prompts.
- `src/rag/vector_store.py`: Chroma persistente; alteração no hash da base/modelo/params invalida o índice e provoca rebuild.
- `src/rag/prompt_rag.py`: o texto de sistema é enviado em papel `system`, não misturado à pergunta do usuário.
- `src/rag/pipeline.py`: valida JSON pelo schema Pydantic da Sprint 3 antes de publicar a resposta; uma saída inválida é sinalizada e não é apresentada como resposta estruturada válida.
- `src/rag/citations.py`: vários chunks da mesma página compartilham o mesmo ID; o rodapé de fontes impede resposta apoiada em contexto sem referência documental visível.
- `app/streamlit_app.py`: interface obrigatória com resposta, campos Pydantic e painel de fontes.

## Origem e manual oficial

A base foi construída sobre a Sprint 3 `sprint3_profissional` do EnergiaLar, do professor Jorge; não usa ChargeGrid Intelligence/Lucas como projeto-base. Antes da avaliação final, baixe o manual oficial `00_manual_oficial_goodwe_hca_g2_en.pdf` e, se disponível, a lista complementar `00b_compatibilidade_goodwe_ev_hca_g2_en.pdf` via `scripts/baixar_manual_oficial.ps1`; depois rode o build do índice.

## Limite conhecido

A configuração usa `gemma4:31b` no chat Cloud e `nomic-embed-text` no endpoint local, porque a API pública Ollama Cloud não oferece embeddings. Isso é um desvio literal do PDF, documentado explicitamente; `python -m src.rag.check_setup` avisa sobre ele e não imprime a chave.


## Correção de recuperação legal (21/10/2026)

A recuperação principal usa `TOP_K=8` por padrão. Para perguntas sobre leis estaduais/municipais e recarga em condomínio, `src/rag/retriever.py` executa uma consulta semântica complementar específica para o art. 2º da Lei Estadual SP nº 18.403/2026. Um trecho adicional é aceito apenas se contiver evidência textual conjunta de artigo 2º, capacidade mínima e instalação futura, evitando incluir texto que negue esse requisito. A busca complementar não chama o modelo de chat nem cria conteúdo; acrescenta um trecho encontrado no índice local. Testes de regressão cobrem o acréscimo, o não uso em perguntas não legais e a rejeição de um trecho contraditório.

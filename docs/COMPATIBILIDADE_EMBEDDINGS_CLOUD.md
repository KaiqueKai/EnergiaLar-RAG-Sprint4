# Compatibilidade: embeddings Ollama Cloud vs. `nomic-embed-text`

**Data da verificação documental:** 23/10/2026. O teste HTTP 401 é o resultado registrado anteriormente pelo usuário; ele não foi repetido nesta revisão.

## Evidências verificadas

- O enunciado da Sprint 4 pede `nomic-embed-text` em ChromaDB e menciona Ollama Cloud.
- O chat deste projeto já respondeu `EnergiaLar OK` com `gemma4:31b` e `https://ollama.com` no teste executado pelo usuário.
- O teste de embeddings contra `https://ollama.com` retornou `401 Unauthorized`. Esse resultado foi observado na conta do projeto, não inferido.
- A documentação oficial de Cloud do Ollama mostra a API `/api/chat`: https://docs.ollama.com/cloud .
- A documentação oficial de embeddings mostra exemplos via endpoint local `http://localhost:11434/api/embed`: https://docs.ollama.com/api/embed .
- A integração de embeddings do LangChain instrui instalar/usar uma instância Ollama local: https://docs.langchain.com/oss/python/integrations/embeddings/ollama .
- Um colaborador do Ollama respondeu na issue #14496 que não há modelos de embedding no Cloud; a issue foi encerrada em 12/03/2026: https://github.com/ollama/ollama/issues/14496 .
- A solicitação #17129 para expor embeddings/reranking Cloud foi aberta em 11/07/2026 e ainda aparece aberta: https://github.com/ollama/ollama/issues/17129 .

## Decisão técnica

Manter `gemma4:31b` no Ollama Cloud, pois o chat já foi verificado com sucesso. Manter o modelo de embedding pedido (`nomic-embed-text`), mas gerar embeddings por Ollama local (`http://localhost:11434`). Assim o pipeline RAG fica executável, com índice vetorial persistente e o mesmo encoder para indexação e consulta.

**Desvio declarado:** a configuração de embeddings não cumpre literalmente o trecho `Ollama Cloud` do enunciado, porque o endpoint público atual não disponibiliza embeddings. Não apresentar o desvio como conformidade plena. A alternativa foi escolhida para obter um RAG funcional, em vez de um RAG que falha na indexação; a limitação é registrada no README, no relatório e na interface.

## Configuração

```dotenv
OLLAMA_HOST=https://ollama.com
CHAT_MODEL=gemma4:31b
EMBEDDING_HOST=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
```

No Windows: instalar o aplicativo oficial Ollama, iniciar o serviço e rodar `ollama pull nomic-embed-text`. Depois execute `python -m src.rag.check_setup`. A chave fica somente no `.env`; nunca registre seu valor.

## Modelo de comparação na avaliação de chat

`gemma4:31b` é o modelo principal do RAG e já respondeu corretamente no teste real executado pelo grupo. O segundo modelo previsto para comparação é `gpt-oss:20b`, que também aparece na configuração histórica da Sprint 3. O registro oficial do modelo Cloud mostra dois nomes distintos: `gpt-oss:20b-cloud` para o comando CLI e `gpt-oss:20b` no campo `model` das chamadas diretas a `https://ollama.com/api/chat` (exemplo oficial: https://ollama.com/library/gpt-oss%3A20b-cloud). Portanto, a configuração da aplicação usa `gpt-oss:20b`, sem sufixo. A disponibilidade atual na conta não é presumida: execute `python -m src.rag.check_models` para fazer uma chamada curta por modelo antes da avaliação em oito casos. Se a conta rejeitar o segundo identificador, registre o erro exato e valide um identificador Cloud vigente antes de substituí-lo. Falha de conexão não é score de qualidade. O registro oficial apresenta preços por milhão de tokens; verifique a página de modelos/uso da sua conta antes da comparação extensa.


## Alternativa Colab (adicionada em 22/10/2026)

O notebook complementar roda `nomic-ai/nomic-embed-text-v1.5` da Hugging Face via Sentence Transformers dentro do runtime hospedado pelo Google Colab; o chat continua na API do Ollama Cloud. Isso transfere o processamento de embeddings para uma VM cloud e evita instalar embeddings na máquina Windows, mas não transforma o runtime em um endpoint gerenciado do Ollama Cloud.

A documentação atual do Ollama Cloud apresenta o endpoint de chat e a configuração `OLLAMA_API_KEY` ([docs](https://docs.ollama.com/cloud)); a API de embeddings continua exemplificada na interface Ollama local ([docs](https://docs.ollama.com/api/embed)). A issue #14496 recebeu resposta de colaborador do Ollama em 27/02/2026 afirmando que não há modelos de embedding no Ollama Cloud, e a solicitação #17129 para disponibilizar embeddings cloud permanece aberta na verificação de 22/10/2026: https://github.com/ollama/ollama/issues/14496 e https://github.com/ollama/ollama/issues/17129. O model card da Nomic define os prefixos de tarefa `search_document:` e `search_query:` para recuperação: https://huggingface.co/nomic-ai/nomic-embed-text-v1.5.

**Como declarar:** o Colab usa embeddings em infraestrutura cloud (runtime do Colab), porém a conformidade literal com `nomic-embed-text` disponibilizado no Ollama Cloud não pode ser afirmada. Se a rubrica exigir estritamente o provedor Ollama Cloud também para embeddings, pedir ao professor confirmação desta alternativa.

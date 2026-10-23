# Versão Google Colab — EnergiaLar Sprint 4

## Arquivos
- `EnergiaLar_Sprint4_Colab.ipynb`: notebook RAG end-to-end de demonstração.
- `EnergiaLar_Conhecimento_Base.zip`: base Markdown/CSV e prompt v3 para upload na primeira execução.

## Execução
1. Envie o `.ipynb` ao Google Colab e abra.
2. Se puder, escolha Runtime → Change runtime type → GPU.
3. Execute as células em ordem.
4. Quando a célula pedir, carregue `EnergiaLar_Conhecimento_Base.zip`.
5. Configure o segredo `OLLAMA_API_KEY` em Colab → Secrets ou use o campo de entrada oculta.
6. O notebook baixa os PDFs oficiais GoodWe, carrega `nomic-ai/nomic-embed-text-v1.5` no runtime hospedado, cria ChromaDB e consulta `gemma4:31b` pelo Ollama Cloud.

## Limite importante
O modelo de embeddings roda na VM hospedada do Colab, não na máquina Windows. Não é o endpoint gerenciado de embeddings do Ollama Cloud, que a documentação/issues consultadas indicam não disponível publicamente no momento. A versão principal Windows mantém a configuração testada `nomic-embed-text` local + chat Ollama Cloud.

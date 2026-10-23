# Testes e comandos — EnergiaLar Sprint 4

Este ZIP já contém a base do EnergiaLar da Sprint 3 integrada com a camada RAG da Sprint 4. Não copie o conteúdo para outra pasta e não crie o novo repositório antes dos testes finais. Use o PowerShell dentro da raiz deste projeto.

## 1. Instalação (Python 3.13)

```powershell
py -3.13 --version
if (-not (Test-Path ".venv\Scripts\python.exe")) { py -3.13 -m venv .venv }
$py = ".\.venv\Scripts\python.exe"
& $py -m pip install --upgrade pip
& $py -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "A instalação falhou" }
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

## 2. Testes locais sem API

Na revisão do projeto ativo no Windows, após corrigir a recuperação Q04 e fortalecer o prompt v3, a saída foi `48 passed in 1.24s`. Esse resultado corresponde ao projeto ativo naquele momento. Reexecute a suíte se aplicar novas alterações de código; a próxima avaliação semântica não exige repetir os testes offline.

```powershell
& $py -m compileall -q src evals app scripts tests
if ($LASTEXITCODE -ne 0) { throw "A compilação falhou" }
& $py -m pytest -q
```

## 3. Setup remoto (pode consumir 1 chamada de chat)

```powershell
& $py -m src.rag.check_setup
```

Anote a saída completa, sem a chave. O chat Cloud já respondeu OK; embeddings Cloud retornaram 401. Instale Ollama local e configure só as variáveis de embeddings com:

```powershell
& $py scripts/configurar_embeddings_locais.py
ollama pull nomic-embed-text
& $py -m src.rag.check_setup
```

O desvio literal do PDF está documentado em `docs/COMPATIBILIDADE_EMBEDDINGS_CLOUD.md`.

## 4. Validar os dois modelos de chat

```powershell
& $py -m src.rag.check_models
```

O modelo principal permanece `gemma4:31b`. O segundo é `gpt-oss:20b`, usando o identificador de API direta (o alias CLI de Cloud é `gpt-oss:20b-cloud`). A chamada curta pode consumir uma pequena quantidade de uso Cloud. Se o segundo falhar, registre a falha sem pontuá-la como qualidade.

## 5. Baixar manual oficial, indexar e abrir interface

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\baixar_manual_oficial.ps1
& $py -m src.rag.build_index --force
& $py -m streamlit run app/streamlit_app.py
```

## 6. Avaliação RAG

Piloto (2 chamadas):
```powershell
& $py -m evals.run_eval --mode iterations --model gemma4:31b --ids Q01 --interactive
```

Comparação após as correções Q04/Q05 (v2 × v3, 16 chamadas):
```powershell
& $py -m evals.run_eval --mode iterations --model gemma4:31b --prompts v2 v3
& $py -m evals.summarize_results --mode iterations
& $py -m evals.exportar_revisao_assistente
```
O modo sem `--interactive` deixa scores manuais em branco por design. A exportação Markdown preserva resposta, fontes e contexto para revisão; depois, registrar a avaliação pela rubrica sem inventar números.

Dois modelos (16 chamadas):
```powershell
& $py -m evals.run_eval --mode models --models gemma4:31b gpt-oss:20b --interactive
& $py -m evals.summarize_results --mode models
```

Matriz opcional dos dois modelos e dois prompts (32 chamadas com oito casos) após os modelos passarem no teste de conectividade. O uso de dois modelos no mesmo provedor não é afirmado como bônus multi-provider se o professor interpretar esse termo literalmente:

```powershell
& $py -m evals.run_eval --mode models --models gemma4:31b gpt-oss:20b --prompts v1 v2 --interactive
& $py -m evals.summarize_results --mode models
```

Para cada resposta, pontue qualidade do contexto, faithfulness e answer relevancy de acordo com `evals/manual_rubric.md`; a presença da citação fica registrada automaticamente quando uma fonte foi recuperada. Só declare melhoria quando os scores reais demonstrarem ganho no mesmo conjunto.

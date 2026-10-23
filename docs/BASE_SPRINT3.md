# Base real da Sprint 3 - professor Jorge

Repositório público original: https://github.com/KaiqueKai/EnergiaLar

Nesta pasta da Sprint 4, os componentes ativos da Sprint 3 foram mantidos na raiz: `src/chatbot.py`, `src/chain/`, `src/guardrails/`, `src/schemas/`, os prompts `system_prompt_v1/v2/v3.md` e os casos/avaliadores conversacionais em `evals/`. A camada nova da Sprint 4 fica em `src/rag/`, `app/`, `data/knowledge_base/` e arquivos de avaliação próprios.

O ZIP local `docs/sprint3_local_snapshot/sprint_3_jorge_profissional_original.zip` é o pacote histórico recebido anteriormente, menor/mais antigo que a árvore pública do repositório. Ele é preservado apenas para rastreabilidade, não é usado como substituto do código público mais completo.

## Ajuste para teste local

Em `src/chain/builder.py`, a checagem da chave é feita ao criar o modelo, em vez de falhar no import do módulo. Isso permite executar testes unitários simulados sem chave e sem chamada de rede. A chamada real continua exigindo `OLLAMA_API_KEY`.

## Limite de proveniência

O manual oficial do fabricante e os resultados de avaliação antigos são arquivos externos do repositório/fabricante, não são recriados artificialmente. O manual precisa ser baixado com o script documentado. O baseline Sprint 3 pode ser reexecutado via `python -m evals.sprint3_eval`; os resultados qualitativos devem ser avaliados manualmente.

## Resultados históricos

O JSON histórico completo da Sprint 3 pode ser obtido diretamente do repositório público com `scripts/baixar_historico_sprint3.ps1`. O script salva como `evals/sprint3_results_historico_publico.json` e não sobrescreve a saída que a equipe gerar localmente. A data registrada no arquivo público é `2026-09-20T15:07:38`; os campos qualitativos estavam marcados como `PREENCHER_MANUALMENTE`, por isso não os tratamos como avaliação final.

# Versionamento do System Prompt — EnergiaLar

## v1 — Rascunho inicial
Arquivo: `system_prompt_v1.md`

Prompt em Markdown com seções por título (Papel, Escopo, Segurança, Prompt
Injection, Formato), sem tagueamento estruturado. Define o domínio e as
regras básicas de segurança, mas o campo `OBJETIVO` não é explícito e a
seção de formato de saída não referencia o schema Pydantic de forma
integrada ao prompt real usado no código.

## v2 — Objetivo explícito e integração com o schema
Arquivo: `system_prompt_v2.md`

Adiciona a seção `Objetivo`, separada do `Papel`, deixando claro para o
modelo qual é a meta de cada resposta (não só quem ele é). A seção de formato
passa a referenciar explicitamente o schema `ConsultaRecarga`.

## v3 — Produção (context engineering com XML tagging)
Arquivo: `system_prompt_v3.md` — **versão carregada por `src/chain/builder.py`**

Reestruturado em 6 blocos com XML tagging (Aula 04 — context engineering leve):
`<identidade>`, `<objetivo>`, `<escopo>`, `<restricoes>`, `<formato_saida>`,
`<escalonamento>`. O bloco `<formato_saida>` recebe `{format_instructions}`
preenchido dinamicamente pelo `PydanticOutputParser` em tempo de execução —
o prompt e o schema ficam sincronizados.

### O que mudou e por quê

| Mudança | Motivo |
|---|---|
| Separação de `<objetivo>` de `<identidade>` (v1 → v2) | Deixa explícito o que o modelo deve alcançar, não só quem ele é |
| Tagueamento XML (v2 → v3) | Estrutura visual de contexto e manutenção do prompt |
| Bloco `<escalonamento>` próprio | Facilita explicitar quando encaminhar para um profissional humano |
| `{format_instructions}` no prompt real | O prompt carregado em execução permanece ligado ao schema Pydantic |

As contagens de tokens devem ser medidas no ambiente da entrega com `python prompts/medir_tokens.py`; não use estimativas como medição real.

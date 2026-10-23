# Revisão de fontes externas e rastreabilidade

**Verificação em:** 21/10/2026. Este documento registra o que foi confirmado nas fontes consultadas; não substitui os documentos oficiais integrais nem dá parecer jurídico/elétrico.

## 1. GoodWe HCA G2 — fonte primária do fabricante

- Página oficial de downloads da linha HCA G2: https://br.goodwe.com/download-hca-g2-series
- Página da linha HCA G2: https://br.goodwe.com/carregadores-hca-g2-goodwe
- Ficha técnica oficial, PDF hospedado no domínio GoodWe: https://br.goodwe.com/Api/downloadFile?id=3931&mid=60&type=1
- Manual oficial HCA G2 em inglês, listado pela página de downloads como “GW_HCA G2_User Manual-EN”, datado na página de 06/12/2024: https://br.goodwe.com/Api/downloadFile?id=2496&mid=60&type=2
- Lista oficial de compatibilidade de carregadores e inversores, listada na mesma página em 14/08/2026: https://br.goodwe.com/Api/downloadFile?id=4535&mid=60&type=2

A ficha técnica consultada identifica os modelos GW7K-HCA-20 (potência nominal de saída de 7.000 W, 230 V, 32 A), GW11K-HCA-20 (11.000 W, 400 V, 16 A) e GW22K-HCA-20 (22.000 W, 400 V, 32 A). Estes valores descrevem dados nominais publicados, não garantem potência real de uma instalação. A ficha técnica também informa proteção residual integrada AC 30 mA + DC 6 mA e necessidade de RCD Tipo A externo; isso não deve ser convertido em instrução personalizada de instalação.

**Limite de pacote:** o PDF binário do manual exato não pôde ser baixado pelo ambiente de preparação (a ferramenta de consulta rejeitou o tipo `application/octet-stream` e o ambiente local não resolveu o DNS do host externo). Portanto, o manual oficial não foi inventado nem substituído por Markdown. O script `scripts/baixar_manual_oficial.ps1` usa os links oficiais. A indexação final permanece bloqueada até o grupo baixar e validar o manual original.

## 2. Tarifas — Enel Distribuição São Paulo

- Página oficial: https://www.enel.com.br/pt-saopaulo/Para_Voce/tarifa-energia-eletrica.html
- A página consultada informa Resolução Homologatória ANEEL nº 3.596/2026, de 30/06/2026, com vigência a partir de 04/07/2026.
- Para B1 residencial convencional, a tabela apresenta TUSD de R$ 472,42/MWh e TE-BVD de R$ 316,96/MWh; as conversões documentadas são R$ 0,47242/kWh e R$ 0,31696/kWh.

Esses valores são **componentes** da tarifa publicada para a distribuidora/classe/modalidade indicada, não o valor total da fatura e não uma tarifa nacional. A tabela didática `04_tarifas_referencia.csv` com R$ 0,85/kWh e R$ 1,05/kWh é simulada e deve continuar rotulada como tal.

## 3. Legislação sobre recarga em condomínios — escopo jurisdicional

- Lei Estadual SP nº 18.403, de 18/02/2026, texto da Assembleia Legislativa: https://al.sp.gov.br/repositorio/legislacao/lei/2026/lei-18403-18.02.2026.html
- Lei Municipal de São Paulo nº 17.336, de 30/03/2020, catálogo oficial: https://legislacao.prefeitura.sp.gov.br/lei-17336-de-30-de-marco-de-2020

A Lei Estadual nº 18.403/2026 trata, entre outros aspectos, da instalação individual em vaga privativa, com requisitos de capacidade elétrica, conformidade técnica, profissional habilitado com ART/RRT e comunicação prévia; ela não autoriza extrapolar automaticamente para qualquer desenho de carregamento compartilhado. A Lei Municipal nº 17.336/2020 é específica ao Município de São Paulo e menciona solução de recarga e medição/cobrança individualizada; o texto traz cronograma que inclui projetos de novas edificações. O corpus não deve afirmar que qualquer lei paulista cria uma obrigação universal de retrofit para todos os condomínios.

`03_condominio_protocolo_orientativo.md` é uma proposta acadêmica, não lei nem regimento aprovado. Para um caso real, confirme a jurisdição, texto legal vigente, distribuidora, normas técnicas e situação concreta com profissionais habilitados.

## 4. Ollama Cloud e embeddings

- Documentação de Cloud: https://docs.ollama.com/cloud — orienta que, nas chamadas diretas à API, o campo `model` use o nome retornado pela listagem da API.
- Documentação de embeddings: https://docs.ollama.com/api/embed — os exemplos oficiais usam `http://localhost:11434/api/embed`.
- Issue #14496, com resposta de colaborador declarando indisponibilidade de modelos de embedding no Cloud e ausência de cronograma público: https://github.com/ollama/ollama/issues/14496
- Issue #17129 sobre disponibilizar embedding/reranking no Cloud: https://github.com/ollama/ollama/issues/17129

O grupo testou `https://ollama.com` na configuração de embeddings e recebeu `401 Unauthorized`, enquanto o chat `gemma4:31b` respondeu `EnergiaLar OK`. A documentação consultada descreve embeddings por endpoint local `http://localhost:11434/api/embed`; a configuração alternativa usa `nomic-embed-text` local e mantém o chat no Cloud. **Essa alternativa não cumpre literalmente o trecho do enunciado que associa embeddings ao Ollama Cloud.** A diferença é mantida explícita em README, relatório e interface; nunca rotular o projeto como conformidade total desse item.

## 5. Modelos e avaliação

- Registro oficial do modelo de comparação gpt-oss Cloud: https://ollama.com/library/gpt-oss%3A20b-cloud. A página mostra `gpt-oss:20b-cloud` como alias CLI e exemplos de API direta usando `gpt-oss:20b`; a página consultada lista preços de US$ 0,07 por milhão de tokens de entrada, US$ 0,035 por milhão de tokens de entrada em cache e US$ 0,30 por milhão de tokens de saída. Preços/limites podem mudar; confirme na conta antes de executar a bateria.
- O modelo RAG principal `gemma4:31b` permanece selecionado porque foi testado com sucesso no ambiente do grupo.
- A disponibilidade atual do segundo modelo deve ser confirmada com uma chamada curta de `python -m src.rag.check_models`. Ter um modelo listado não comprova que a conta, chave, rota e identificador escolhidos funcionam no momento.
- Não há scores novos da Sprint 4 nesta pasta até que os comandos de avaliação sejam executados. A rubrica manual de `faithfulness`, `answer_relevancy` e qualidade do contexto é um fallback permitido pelo enunciado; não deve ser chamada de resultado RAGAS. O delta só pode ser reportado após comparar as mesmas perguntas e critérios numa execução comparável.

## 6. Limite técnico e evidência

As verificações de páginas públicas confirmam os fatos resumidos acima. Não foi possível baixar o arquivo binário oficial do manual diretamente para este pacote; o link e o script são fornecidos para baixar a fonte original no computador do grupo. O teste automatizado do gate rejeita arquivo ausente, conteúdo que não seja PDF e PDF sem estrutura/texto legíveis. Nenhuma métrica de avaliação, contribuição individual de equipe ou resultado de conectividade do segundo modelo foi inventado.

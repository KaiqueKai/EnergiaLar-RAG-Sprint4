# FAQ — EnergiaLar, recarga e eficiência energética

## O que representa o projeto da Sprint 3?

A Sprint 3 do EnergiaLar é uma prova de conceito de assistente conversacional para apoiar perguntas relacionadas à operação e eficiência energética de estações de recarga de veículos elétricos. O código examinado usa LCEL, prompt externo, histórico por sessão e validação de saída com Pydantic v2. A Sprint 3 não constitui, por si só, uma ligação de telemetria a um carregador físico.

**Fonte do projeto:** repositório do grupo, EnergiaLar: https://github.com/KaiqueKai/EnergiaLar

## Qual é a diferença entre kW e kWh?

- kW (quilowatt) mede potência, isto é, uma taxa de transferência de energia.
- kWh (quilowatt-hora) mede energia acumulada ao longo do tempo.
- Em um cenário ideal de potência constante, 7 kW durante 1 hora correspondem a 7 kWh. Em uma sessão real, limites do veículo/carregador e perdas podem alterar o valor efetivo.

A relação ideal é `energia (kWh) = potência média (kW) × duração (h)`. Para uma sessão real, consulte os dados medidos pelo equipamento ou medidor correspondente.

## Como estimar o custo de uma sessão?

A fórmula didática é `custo estimado (R$) = energia (kWh) × tarifa aplicável (R$/kWh)`. O custo real depende da distribuidora, categoria, modalidade, componentes da fatura e condições vigentes. Os preços da tabela de demonstração nesta base são simulados e não devem ser tratados como tarifa oficial.

## O carregador HCA G2 pode integrar-se a um sistema fotovoltaico?

A página oficial da GoodWe descreve integração do HCA G2 com inversor e bateria do sistema fotovoltaico, além de modos de carregamento configuráveis no aplicativo SEMS+. A compatibilidade de um conjunto específico deve ser confirmada no manual/lista de compatibilidade atuais dos modelos envolvidos.

**Fonte primária:** GoodWe Brasil, Linha HCA G2: https://br.goodwe.com/carregadores-hca-g2-goodwe

## Quais são os limites elétricos de uma instalação?

Não é possível dimensionar uma instalação apenas pelo número de carregadores ou por uma resposta de chatbot. São necessários dados do local, alimentação, circuitos, proteções, demanda, equipamento e condições de instalação. Este assistente não deve prescrever bitola, disjuntor ou proteção elétrica; encaminhe a decisão ao projeto técnico, manual do modelo exato e profissional habilitado.

## O projeto controla um carregador físico?

Não há, nesta versão, integração com telemetria de um carregador GoodWe físico. Respostas sobre medições, sessões e valores não devem ser descritas como dados de equipamento real sem uma integração implementada e evidenciada.

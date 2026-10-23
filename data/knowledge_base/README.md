# Base de conhecimento — EnergiaLar / Sprint 4

- `00_manual_oficial_goodwe_hca_g2_en.pdf`: manual oficial HCA G2 em inglês, listado na página GoodWe Brasil. O binário está incluído no pacote atual e o gate exige que o PDF exista e passe pela validação antes de indexar. Em uma instalação limpa ou para atualizar uma revisão, use o script oficial de download.
- `00b_compatibilidade_goodwe_ev_hca_g2_en.pdf`: lista oficial GoodWe de compatibilidade de carregadores EV e inversores, listada na página HCA G2 e atualizada em 14/08/2026; fonte complementar importante. O binário está incluído no pacote atual. O script tenta baixá-lo/validá-lo como documento complementar, sem substituir a exigência do manual obrigatório.
- `01_folha_dados_hca_g2.md`: resumo acadêmico claramente identificado, ligado às páginas oficiais GoodWe; não se apresenta como manual oficial.
- `02_faq_energialar_recarga.md`: FAQ do domínio e do projeto, com limites entre simulação e operação real.
- `03_condominio_protocolo_orientativo.md`: protocolo-modelo acadêmico, não é regimento aprovado nem orientação jurídica.
- `04_tarifas_referencia.csv`: preços didáticos marcados como simulados e referências para consultar tarifa vigente.
- `05_perguntas_de_validacao.md`: regras de escopo e casos de uso seguro.
- `06_referencias_condominiais_sp.md`: resumo acadêmico, com links oficiais, da Lei Estadual SP 18.403/2026 e da Lei Municipal SP 17.336/2020; deixa explícitos escopo e limites. Não é um regimento condominial real nem substitui legislação integral.

Documentos novos devem vir de fonte autorizada, ter origem e data de consulta registradas, e nunca conter segredos ou dados pessoais. Após adicionar/alterar a base, execute `python -m src.rag.build_index --force`. O último build observado no workspace Windows gerou 174 chunks; esse número deve ser revalidado se os arquivos ou parâmetros forem alterados.

- `07_tarifas_oficiais_enel_sp_2026.md` e `.csv`: componentes tarifários oficiais publicados pela Enel SP com vigência informada a partir de 04/07/2026; não são tarifa nacional nem custo total da fatura.

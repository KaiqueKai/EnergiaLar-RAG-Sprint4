from __future__ import annotations
import streamlit as st
from src.rag.settings import CHAT_MODEL, COMPARISON_MODELS, TOP_K, MIN_RELEVANCE_SCORE, EMBEDDING_MODEL, EMBEDDING_HOST, OLLAMA_HOST
from src.rag.vector_store import build_or_load_vector_store
from src.rag.pipeline import answer_question
from src.rag.security import redact_sensitive_text
from src.rag.settings import OLLAMA_API_KEY

st.set_page_config(page_title="EnergiaLar | Assistente RAG", page_icon="⚡", layout="wide")

st.title("EnergiaLar")
st.subheader("Assistente documental para recarga de veículos elétricos")
st.caption("Sprint 4 · RAG com ChromaDB persistente · Fontes visíveis · Dados simulados identificados")

with st.sidebar:
    st.header("Configuração da consulta")
    selected_model = st.selectbox(
        "Modelo de chat",
        options=list(dict.fromkeys([CHAT_MODEL, *COMPARISON_MODELS, "gpt-oss:20b", "gemma4:31b"])),
        index=0,
    )
    prompt_version = st.selectbox("Versão do prompt", options=["v3", "v2", "v1"], index=0,
                                  help="v1 = baseline; v2 = guardrails explícitos; v3 = checklist estrito de evidência, citações e validação.")
    top_k = st.slider("Documentos candidatos (top-k)", min_value=1, max_value=8, value=max(1, min(8, TOP_K)))
    min_score = st.slider("Relevância mínima", min_value=0.0, max_value=1.0, value=float(MIN_RELEVANCE_SCORE), step=0.05)
    st.divider()
    st.write(f"**Host de chat:** `{OLLAMA_HOST}`")
    st.write(f"**Host dos embeddings:** `{EMBEDDING_HOST}`")
    st.write(f"**Modelo de embeddings:** `{EMBEDDING_MODEL}`")
    st.caption("A chave é lida do .env; nunca exibida na interface.")
    if st.button("Reconstruir índice Chroma", use_container_width=True):
        with st.spinner("Lendo a base e reconstruindo o índice persistente..."):
            try:
                build_or_load_vector_store(force_rebuild=True)
                st.success("Índice reconstruído.")
            except Exception as exc:
                st.error(f"Não foi possível reconstruir o índice: {exc}")

st.info("O assistente documental responde somente com a base recuperada. Valores da tabela didática não são tarifas oficiais e o projeto não controla um carregador físico.")

with st.form("pergunta_rag", clear_on_submit=False):
    question = st.text_area(
        "Faça uma pergunta sobre a base do EnergiaLar",
        placeholder="Ex.: Quais potências nominais aparecem na linha HCA G2?",
        height=90,
    )
    submitted = st.form_submit_button("Consultar base documental", type="primary")

if submitted:
    if not question.strip():
        st.warning("Digite uma pergunta.")
    else:
        with st.spinner("Recuperando fontes e consultando o modelo..."):
            try:
                response = answer_question(
                    question=question,
                    model_name=selected_model,
                    prompt_version=prompt_version,
                    top_k=top_k,
                    min_score=min_score,
                )
                st.session_state["last_rag_response"] = response
                st.session_state["last_rag_question"] = question
            except Exception as exc:
                safe_detail = redact_sensitive_text(f"{type(exc).__name__}: {exc}", OLLAMA_API_KEY)
                st.error(
                    "A consulta falhou. Confira a chave em .env, a disponibilidade do modelo e o teste de embeddings. "
                    f"Detalhe técnico (credenciais redigidas): {safe_detail}"
                )

response = st.session_state.get("last_rag_response")
if response:
    st.divider()
    if response.get("security_events"):
        st.warning("Uma cláusula de instrução suspeita foi removida antes da recuperação. O sistema processou apenas a parte segura da pergunta.")
    st.markdown("### Resposta")
    st.markdown(response["answer"])
    structured = response.get("structured_answer") or {}
    if structured:
        with st.expander("Campos estruturados (Pydantic v2)"):
            st.json(structured)
            st.caption(f"Validação do contrato: {'OK' if response.get('structure_valid') else 'FALHOU'}")
    st.caption(
        f"Modelo: {response['model']} · Prompt: {response['prompt_version']} · "
        f"Maior score de recuperação: {response['relevance'] if isinstance(response['relevance'], (int, float)) else response['relevance']}"
    )
    st.markdown("### Fontes recuperadas")
    if response["sources"]:
        for source in response["sources"]:
            label = source["citation"]
            score_text = f" · score {source['score']:.3f}" if isinstance(source.get("score"), (int, float)) else ""
            with st.expander(label + score_text, expanded=False):
                st.write(source["excerpt"])
                if source.get("url"):
                    st.markdown(f"Fonte primária: {source['url']}")
    else:
        st.write("Nenhuma fonte ultrapassou o limite de relevância; o sistema recusou extrapolar a base.")
    if st.button("Limpar resposta"):
        st.session_state.pop("last_rag_response", None)
        st.session_state.pop("last_rag_question", None)
        st.rerun()

st.divider()
with st.expander("Sobre a base e os limites do protótipo"):
    st.markdown(
        """
        - A folha de dados em Markdown é um resumo acadêmico ligado à página oficial GoodWe; não substitui o manual oficial. Adicione o manual oficial usando scripts/baixar_manual_oficial.ps1 antes da entrega final.
        - O procedimento de condomínio é uma proposta acadêmica, não uma norma legal.
        - A tabela contém preços simulados para exercícios de cálculo; tarifas reais devem ser verificadas na fatura/distribuidora.
        - A Sprint 3 do projeto usa simulação por software; não existe conexão física com carregador neste pacote.
        - Perguntas fora da base devem receber recusa explícita, sem especificações inventadas.
        """
    )

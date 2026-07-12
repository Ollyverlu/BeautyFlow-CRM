import streamlit as st
from urllib.parse import quote


# ================= DADOS DE CONTATO =================
WHATSAPP = "5521988219493"

INSTAGRAM = "https://www.instagram.com/lucianaollyver"


# ================= PÁGINA CONTATOS =================
def mostrar_contatos():

    st.title("📱 WhatsApp e Instagram")

    st.subheader("💄 Luciana Ollyver")

    st.write(
        "Entre em contato para informações, "
        "serviços e agendamentos."
    )

    st.markdown("---")

    # ================= WHATSAPP =================
    mensagem = quote(
        "Olá, Luciana! Quero saber mais sobre os serviços de beleza."
    )

    link_zap = (
        f"https://wa.me/{WHATSAPP}"
        f"?text={mensagem}"
    )

    st.link_button(
        "💬 Falar no WhatsApp",
        link_zap
    )

    # ================= INSTAGRAM =================
    st.link_button(
        "📸 Abrir Instagram",
        INSTAGRAM
    )

    st.markdown("---")

    st.info(
        "Atendimento mediante agendamento."
    )
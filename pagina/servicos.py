import streamlit as st
from urllib.parse import quote


# ================= DADOS DO WHATSAPP =================
WHATSAPP = "5521988219493"


# ================= FUNÇÃO WHATSAPP =================
def link_whatsapp(servico, valor):

    mensagem = (
        f"Olá, Luciana! Tenho interesse em agendar o serviço: "
        f"{servico}. Valor: {valor}."
    )

    return f"https://wa.me/{WHATSAPP}?text={quote(mensagem)}"


# ================= LISTA DE SERVIÇOS =================
servicos = {

    "Extensão de Cílios": [
        ("Extensão de Cílios", "R$ 120,00"),
        ("Manutenção de Cílios", "R$ 80,00"),
    ],

    "Mechas": [
        ("Balayagem", "R$ 250,00"),
        ("Strong", "R$ 280,00"),
        ("Morena Iluminada", "R$ 300,00"),
        ("Retoque de Mechas", "R$ 180,00"),
    ],

    "Cabelo": [
        ("Corte de Cabelo", "R$ 60,00"),
        ("Escova Curta", "R$ 50,00"),
        ("Escova Média", "R$ 70,00"),
        ("Escova Longa", "R$ 90,00"),
    ],

    "Tratamentos": [
        ("Hidratação", "R$ 80,00"),
        ("Reconstrução", "R$ 100,00"),
        ("Nutrição", "R$ 90,00"),
        ("Progressiva sem Formol", "R$ 180,00"),
        ("Botox", "R$ 150,00"),
    ],

    "Micropigmentação": [
        ("Micropigmentação Esfumada", "R$ 350,00"),
        ("Micropigmentação Fio a Fio", "R$ 400,00"),
    ]
}


# ================= PÁGINA SERVIÇOS =================
def mostrar_servicos():

    st.title("💅 Serviços e Valores")

    categoria = st.selectbox(
        "Escolha uma categoria:",
        list(servicos.keys())
    )

    st.markdown("---")

    for servico, valor in servicos[categoria]:

        st.subheader(servico)

        st.success(
            f"Valor: {valor}"
        )

        link = link_whatsapp(
            servico,
            valor
        )

        st.link_button(
            "💬 Agendar pelo WhatsApp",
            link
        )

        st.markdown("---")
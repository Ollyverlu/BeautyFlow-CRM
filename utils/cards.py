import streamlit as st


def card(titulo, valor, icone="✨", cor="#B85A6B"):

    st.markdown(f"### {icone} {titulo}")

    st.metric(
        label="",
        value=valor
    )
import streamlit as st
import pandas as pd
from banco import conectar


def mostrar_consultar_dados():

    st.title("📋 Dados Salvos no Sistema")

    conn = conectar()

    # ================= CLIENTES =================
    st.subheader("👩‍💼 Clientes Cadastradas")

    clientes_df = pd.read_sql_query(
        "SELECT * FROM clientes ORDER BY id DESC",
        conn
    )

    if clientes_df.empty:
        st.info("Ainda não existem clientes cadastradas.")
    else:
        st.dataframe(
            clientes_df,
            use_container_width=True
        )

    st.markdown("---")

    # ================= AGENDAMENTOS =================
    st.subheader("📅 Agendamentos Salvos")

    agenda_df = pd.read_sql_query(
        "SELECT * FROM agendamentos ORDER BY id DESC",
        conn
    )

    if agenda_df.empty:
        st.info("Ainda não existem agendamentos salvos.")
    else:
        st.dataframe(
            agenda_df,
            use_container_width=True
        )

    st.markdown("---")

    # ================= PRODUTOS =================
    st.subheader("🛍️ Produtos Cadastrados")

    produtos_df = pd.read_sql_query(
        "SELECT * FROM produtos ORDER BY id DESC",
        conn
    )

    if produtos_df.empty:
        st.info("Ainda não existem produtos cadastrados.")
    else:
        st.dataframe(
            produtos_df,
            use_container_width=True
        )

    st.markdown("---")

    # ================= VENDAS =================
    st.subheader("💰 Vendas Registradas")

    vendas_df = pd.read_sql_query(
        "SELECT * FROM vendas ORDER BY id DESC",
        conn
    )

    if vendas_df.empty:
        st.info("Ainda não existem vendas registradas.")
    else:
        st.dataframe(
            vendas_df,
            use_container_width=True
        )

    conn.close()
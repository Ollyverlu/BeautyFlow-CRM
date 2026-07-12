import streamlit as st
import pandas as pd
from datetime import date
from banco import conectar


def mostrar_caixa():

    st.title("💵 Caixa do Dia")

    st.write(
        "Acompanhe as entradas, saídas e o saldo de uma data específica."
    )

    data_caixa = st.date_input(
        "Escolha a data",
        value=date.today(),
        key="caixa_data"
    )

    conn = conectar()

    # ================= VENDAS DO DIA =================
    vendas_df = pd.read_sql_query(
        """
        SELECT *
        FROM vendas
        WHERE data = ?
        ORDER BY id DESC
        """,
        conn,
        params=(str(data_caixa),)
    )

    # ================= FINANCEIRO DO DIA =================
    financeiro_df = pd.read_sql_query(
        """
        SELECT *
        FROM financeiro
        WHERE data = ?
        ORDER BY id DESC
        """,
        conn,
        params=(str(data_caixa),)
    )

    conn.close()

    # ================= CÁLCULOS =================
    total_vendas = 0.0
    quantidade_itens = 0
    total_entradas = 0.0
    total_saidas = 0.0

    if not vendas_df.empty:

        total_vendas = float(
            vendas_df["valor_total"].sum()
        )

        quantidade_itens = int(
            vendas_df["quantidade"].sum()
        )

    if not financeiro_df.empty:

        entradas_df = financeiro_df[
            financeiro_df["tipo"] == "Entrada"
        ]

        saidas_df = financeiro_df[
            financeiro_df["tipo"] == "Saída"
        ]

        if not entradas_df.empty:

            total_entradas = float(
                entradas_df["valor"].sum()
            )

        if not saidas_df.empty:

            total_saidas = float(
                saidas_df["valor"].sum()
            )

    saldo_dia = total_entradas - total_saidas

    quantidade_vendas = len(vendas_df)

    if quantidade_vendas > 0:

        ticket_medio = total_vendas / quantidade_vendas

    else:

        ticket_medio = 0.0

    # ================= MÉTRICAS =================
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💰 Vendas de Produtos",
        f"R$ {total_vendas:.2f}"
    )

    col2.metric(
        "📦 Itens Vendidos",
        quantidade_itens
    )

    col3.metric(
        "🎯 Ticket Médio",
        f"R$ {ticket_medio:.2f}"
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "💵 Entradas Financeiras",
        f"R$ {total_entradas:.2f}"
    )

    col5.metric(
        "💸 Saídas Financeiras",
        f"R$ {total_saidas:.2f}"
    )

    col6.metric(
        "📈 Saldo do Dia",
        f"R$ {saldo_dia:.2f}"
    )

    st.markdown("---")

    aba1, aba2 = st.tabs([
        "🧾 Vendas do Dia",
        "📋 Movimentos Financeiros"
    ])

    # ================= VENDAS =================
    with aba1:

        st.subheader("🧾 Vendas Registradas")

        if vendas_df.empty:

            st.info(
                "Não existem vendas registradas nesta data."
            )

        else:

            st.dataframe(
                vendas_df,
                use_container_width=True
            )

            vendas_produto = vendas_df.groupby(
                "produto"
            )["quantidade"].sum()

            st.subheader(
                "🏆 Produtos Vendidos"
            )

            st.bar_chart(
                vendas_produto
            )

    # ================= FINANCEIRO =================
    with aba2:

        st.subheader("📋 Entradas e Saídas")

        if financeiro_df.empty:

            st.info(
                "Não existem movimentos financeiros nesta data."
            )

        else:

            st.dataframe(
                financeiro_df,
                use_container_width=True
            )

            resumo_tipo = financeiro_df.groupby(
                "tipo"
            )["valor"].sum()

            st.subheader(
                "📊 Resumo do Caixa"
            )

            st.bar_chart(
                resumo_tipo
            )
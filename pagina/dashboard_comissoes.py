from datetime import date

import pandas as pd
import streamlit as st

from banco import conectar


# ==================================================
# FORMATAR MOEDA
# ==================================================
def formatar_moeda(valor):

    texto = f"{float(valor):,.2f}"

    texto = (
        texto
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


# ==================================================
# CARREGAR DADOS DO DIA
# ==================================================
def carregar_resumo_atendimentos():

    hoje = str(date.today())

    conn = conectar()

    try:

        resumo_df = pd.read_sql_query(
            """
            SELECT
                COUNT(*) AS atendimentos,
                COUNT(DISTINCT cliente) AS clientes,
                COUNT(DISTINCT funcionario_id) AS funcionarios,
                IFNULL(SUM(valor_servico), 0) AS faturamento,
                IFNULL(SUM(valor_comissao), 0) AS comissoes,
                IFNULL(SUM(valor_salao), 0) AS valor_salao
            FROM atendimentos_comissoes
            WHERE data = ?
            """,
            conn,
            params=(hoje,)
        )

        funcionario_destaque = pd.read_sql_query(
            """
            SELECT
                funcionario_nome,
                COUNT(*) AS atendimentos,
                IFNULL(SUM(valor_servico), 0) AS faturamento,
                IFNULL(SUM(valor_comissao), 0) AS comissao
            FROM atendimentos_comissoes
            WHERE data = ?
            GROUP BY funcionario_id, funcionario_nome
            ORDER BY faturamento DESC
            LIMIT 1
            """,
            conn,
            params=(hoje,)
        )

        servico_destaque = pd.read_sql_query(
            """
            SELECT
                servico,
                COUNT(*) AS quantidade,
                IFNULL(SUM(valor_servico), 0) AS faturamento
            FROM atendimentos_comissoes
            WHERE data = ?
            GROUP BY servico
            ORDER BY quantidade DESC, faturamento DESC
            LIMIT 1
            """,
            conn,
            params=(hoje,)
        )

        atendimentos_funcionarios = pd.read_sql_query(
            """
            SELECT
                funcionario_nome,
                COUNT(*) AS atendimentos,
                IFNULL(SUM(valor_servico), 0) AS faturamento,
                IFNULL(SUM(valor_comissao), 0) AS comissao,
                IFNULL(SUM(valor_salao), 0) AS valor_salao
            FROM atendimentos_comissoes
            WHERE data = ?
            GROUP BY funcionario_id, funcionario_nome
            ORDER BY faturamento DESC
            """,
            conn,
            params=(hoje,)
        )

    finally:

        conn.close()

    return (
        resumo_df,
        funcionario_destaque,
        servico_destaque,
        atendimentos_funcionarios
    )


# ==================================================
# MOSTRAR PAINEL DE ATENDIMENTOS
# ==================================================
def mostrar_painel_atendimentos_dashboard():

    st.subheader("💇 Movimento do Salão Hoje")

    try:

        (
            resumo_df,
            funcionario_destaque,
            servico_destaque,
            atendimentos_funcionarios
        ) = carregar_resumo_atendimentos()

    except Exception:

        st.info(
            "O painel de atendimentos ficará disponível "
            "após o primeiro atendimento ser registrado."
        )

        return

    if resumo_df.empty:

        st.info(
            "Ainda não existem atendimentos registrados hoje."
        )

        return

    resumo = resumo_df.iloc[0]

    atendimentos = int(
        resumo["atendimentos"] or 0
    )

    clientes = int(
        resumo["clientes"] or 0
    )

    funcionarios = int(
        resumo["funcionarios"] or 0
    )

    faturamento = float(
        resumo["faturamento"] or 0
    )

    comissoes = float(
        resumo["comissoes"] or 0
    )

    valor_salao = float(
        resumo["valor_salao"] or 0
    )

    coluna1, coluna2, coluna3 = st.columns(3)

    coluna1.metric(
        "💇 Atendimentos hoje",
        atendimentos
    )

    coluna2.metric(
        "👩 Clientes atendidas",
        clientes
    )

    coluna3.metric(
        "👩‍💼 Funcionárias trabalhando",
        funcionarios
    )

    coluna4, coluna5, coluna6 = st.columns(3)

    coluna4.metric(
        "💰 Faturamento dos serviços",
        formatar_moeda(faturamento)
    )

    coluna5.metric(
        "👩‍💼 Comissões calculadas",
        formatar_moeda(comissoes)
    )

    coluna6.metric(
        "🏢 Valor do salão",
        formatar_moeda(valor_salao)
    )

    st.markdown("---")

    destaque1, destaque2 = st.columns(2)

    with destaque1:

        st.subheader("🏆 Funcionária Destaque")

        if funcionario_destaque.empty:

            st.info(
                "Nenhuma funcionária possui "
                "atendimento registrado hoje."
            )

        else:

            funcionaria = funcionario_destaque.iloc[0]

            st.write(
                f"### 👩‍💼 {funcionaria['funcionario_nome']}"
            )

            st.write(
                f"💇 **Atendimentos:** "
                f"{int(funcionaria['atendimentos'])}"
            )

            st.write(
                f"💰 **Faturamento gerado:** "
                f"{formatar_moeda(funcionaria['faturamento'])}"
            )

            st.write(
                f"👛 **Comissão:** "
                f"{formatar_moeda(funcionaria['comissao'])}"
            )

    with destaque2:

        st.subheader("⭐ Serviço Destaque")

        if servico_destaque.empty:

            st.info(
                "Nenhum serviço foi registrado hoje."
            )

        else:

            servico = servico_destaque.iloc[0]

            st.write(
                f"### 💅 {servico['servico']}"
            )

            st.write(
                f"📋 **Quantidade:** "
                f"{int(servico['quantidade'])}"
            )

            st.write(
                f"💰 **Faturamento:** "
                f"{formatar_moeda(servico['faturamento'])}"
            )

    if not atendimentos_funcionarios.empty:

        st.markdown("---")

        st.subheader(
            "📊 Resultado por Funcionária"
        )

        tabela = atendimentos_funcionarios.copy()

        tabela["Faturamento"] = tabela[
            "faturamento"
        ].apply(
            formatar_moeda
        )

        tabela["Comissão"] = tabela[
            "comissao"
        ].apply(
            formatar_moeda
        )

        tabela["Valor do Salão"] = tabela[
            "valor_salao"
        ].apply(
            formatar_moeda
        )

        tabela = tabela.rename(
            columns={
                "funcionario_nome": "Funcionária",
                "atendimentos": "Atendimentos"
            }
        )

        st.dataframe(
            tabela[
                [
                    "Funcionária",
                    "Atendimentos",
                    "Faturamento",
                    "Comissão",
                    "Valor do Salão"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        grafico = (
            atendimentos_funcionarios
            .set_index("funcionario_nome")[
                "faturamento"
            ]
        )

        st.bar_chart(
            grafico
        )
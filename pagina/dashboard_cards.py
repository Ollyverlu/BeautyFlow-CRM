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
# BUSCAR INDICADORES REAIS DO DIA
# ==================================================
def carregar_indicadores_do_dia():

    hoje = str(date.today())

    conn = conectar()

    try:

        indicadores_df = pd.read_sql_query(
            """
            SELECT
                COUNT(*) AS atendimentos,
                COUNT(DISTINCT cliente) AS clientes,
                COUNT(DISTINCT funcionario_id) AS funcionarias,
                IFNULL(SUM(valor_servico), 0) AS faturamento,
                IFNULL(SUM(valor_comissao), 0) AS comissoes,
                IFNULL(SUM(valor_salao), 0) AS valor_salao
            FROM atendimentos_comissoes
            WHERE data = ?
            """,
            conn,
            params=(hoje,)
        )

    except Exception:

        indicadores_df = pd.DataFrame(
            {
                "atendimentos": [0],
                "clientes": [0],
                "funcionarias": [0],
                "faturamento": [0.0],
                "comissoes": [0.0],
                "valor_salao": [0.0]
            }
        )

    finally:

        conn.close()

    return indicadores_df.iloc[0]


# ==================================================
# MOSTRAR CARTÕES PREMIUM
# ==================================================
def mostrar_cards_premium():

    dados = carregar_indicadores_do_dia()

    atendimentos = int(
        dados["atendimentos"] or 0
    )

    clientes = int(
        dados["clientes"] or 0
    )

    funcionarias = int(
        dados["funcionarias"] or 0
    )

    faturamento = float(
        dados["faturamento"] or 0
    )

    comissoes = float(
        dados["comissoes"] or 0
    )

    valor_salao = float(
        dados["valor_salao"] or 0
    )

    st.subheader("📊 Indicadores do Dia")

    coluna1, coluna2, coluna3, coluna4 = st.columns(4)

    coluna1.metric(
        "💰 Faturamento",
        formatar_moeda(faturamento)
    )

    coluna2.metric(
        "👩 Clientes atendidas",
        clientes,
        delta=f"{atendimentos} atendimento(s)"
    )

    coluna3.metric(
        "👩‍💼 Funcionárias",
        funcionarias
    )

    coluna4.metric(
        "🏢 Valor do salão",
        formatar_moeda(valor_salao)
    )

    coluna5, coluna6 = st.columns(2)

    coluna5.metric(
        "👛 Comissões calculadas",
        formatar_moeda(comissoes)
    )

    coluna6.metric(
        "💇 Atendimentos realizados",
        atendimentos
    )
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
# CRIAR TABELA DE METAS
# ==================================================
def criar_tabela_metas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS metas_salao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL UNIQUE,
            valor REAL NOT NULL DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO metas_salao
        (
            tipo,
            valor
        )
        VALUES (?, ?)
        """,
        (
            "Meta diária",
            1000.00
        )
    )

    conn.commit()
    conn.close()


# ==================================================
# CARREGAR META
# ==================================================
def carregar_meta_diaria():

    criar_tabela_metas()

    conn = conectar()

    meta_df = pd.read_sql_query(
        """
        SELECT valor
        FROM metas_salao
        WHERE tipo = 'Meta diária'
        LIMIT 1
        """,
        conn
    )

    conn.close()

    if meta_df.empty:
        return 0.0

    return float(
        meta_df.iloc[0]["valor"]
    )


# ==================================================
# CARREGAR FATURAMENTO DE HOJE
# ==================================================
def carregar_faturamento_hoje():

    hoje = str(
        date.today()
    )

    conn = conectar()

    resultado_df = pd.read_sql_query(
        """
        SELECT
            IFNULL(
                SUM(valor_servico),
                0
            ) AS total
        FROM atendimentos_comissoes
        WHERE data = ?
        """,
        conn,
        params=(
            hoje,
        )
    )

    conn.close()

    return float(
        resultado_df.iloc[0]["total"]
    )


# ==================================================
# SALVAR META
# ==================================================
def salvar_meta_diaria(novo_valor):

    criar_tabela_metas()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE metas_salao
        SET valor = ?
        WHERE tipo = 'Meta diária'
        """,
        (
            float(novo_valor),
        )
    )

    conn.commit()
    conn.close()


# ==================================================
# MOSTRAR META NO DASHBOARD
# ==================================================
def mostrar_meta_diaria():

    st.subheader(
        "🎯 Meta do Dia"
    )

    meta_diaria = carregar_meta_diaria()
    faturamento_hoje = carregar_faturamento_hoje()

    if meta_diaria > 0:

        percentual = (
            faturamento_hoje
            / meta_diaria
        )

    else:

        percentual = 0.0

    percentual_barra = min(
        max(
            percentual,
            0.0
        ),
        1.0
    )

    coluna1, coluna2, coluna3 = st.columns(
        3
    )

    coluna1.metric(
        "🎯 Meta",
        formatar_moeda(
            meta_diaria
        )
    )

    coluna2.metric(
        "💰 Realizado",
        formatar_moeda(
            faturamento_hoje
        )
    )

    coluna3.metric(
        "📈 Progresso",
        f"{percentual * 100:.1f}%"
    )

    st.progress(
        percentual_barra
    )

    if percentual >= 1:

        st.success(
            "🏆 Meta diária alcançada! Parabéns à equipe!"
        )

    elif percentual >= 0.75:

        st.info(
            "🌟 Falta pouco para alcançar a meta do dia."
        )

    elif percentual > 0:

        valor_faltante = (
            meta_diaria
            - faturamento_hoje
        )

        st.write(
            f"Faltam **{formatar_moeda(valor_faltante)}** "
            "para atingir a meta."
        )

    else:

        st.info(
            "A meta começará a avançar quando os "
            "atendimentos de hoje forem registrados."
        )

    with st.expander(
        "⚙️ Alterar meta diária"
    ):

        nova_meta = st.number_input(
            "Nova meta diária (R$)",
            min_value=0.0,
            value=float(
                meta_diaria
            ),
            step=100.0,
            format="%.2f",
            key="nova_meta_diaria"
        )

        if st.button(
            "💾 Salvar Meta",
            use_container_width=True,
            key="btn_salvar_meta_diaria"
        ):

            if nova_meta <= 0:

                st.error(
                    "A meta deve ser maior que zero."
                )

            else:

                salvar_meta_diaria(
                    nova_meta
                )

                st.success(
                    "Meta diária atualizada com sucesso!"
                )

                st.rerun()
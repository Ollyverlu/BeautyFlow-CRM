
from datetime import date, datetime

import pandas as pd
import streamlit as st

from banco import conectar


FORMAS_PAGAMENTO = [
    "Dinheiro",
    "Pix",
    "Cartão de Débito",
    "Cartão de Crédito",
    "Transferência",
    "Outro"
]


# ==================================================
# FUNÇÕES DE FORMATAÇÃO
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


def formatar_data_br(valor):

    try:

        data_convertida = datetime.strptime(
            str(valor),
            "%Y-%m-%d"
        )

        return data_convertida.strftime(
            "%d/%m/%Y"
        )

    except (ValueError, TypeError):

        return str(valor)


# ==================================================
# CRIAR TABELA DO CAIXA
# ==================================================
def criar_tabela_caixa():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS caixa_diario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            valor_inicial REAL NOT NULL DEFAULT 0,
            total_entradas REAL NOT NULL DEFAULT 0,
            total_saidas REAL NOT NULL DEFAULT 0,
            saldo_esperado REAL NOT NULL DEFAULT 0,
            valor_contado REAL,
            diferenca REAL,
            responsavel_abertura TEXT,
            responsavel_fechamento TEXT,
            hora_abertura TEXT,
            hora_fechamento TEXT,
            observacao_abertura TEXT,
            observacao_fechamento TEXT,
            status TEXT NOT NULL DEFAULT 'Aberto'
        )
        """
    )

    conn.commit()
    conn.close()


# ==================================================
# BUSCAR CAIXA ABERTO
# ==================================================
def buscar_caixa_aberto():

    criar_tabela_caixa()

    conn = conectar()

    caixa_df = pd.read_sql_query(
        """
        SELECT *
        FROM caixa_diario
        WHERE status = 'Aberto'
        ORDER BY id DESC
        LIMIT 1
        """,
        conn
    )

    conn.close()

    return caixa_df


# ==================================================
# CARREGAR HISTÓRICO
# ==================================================
def carregar_historico_caixa():

    criar_tabela_caixa()

    conn = conectar()

    historico_df = pd.read_sql_query(
        """
        SELECT *
        FROM caixa_diario
        ORDER BY data DESC, id DESC
        """,
        conn
    )

    conn.close()

    return historico_df


# ==================================================
# CALCULAR MOVIMENTOS DO DIA
# ==================================================
def calcular_movimentos(data_caixa):

    conn = conectar()

    financeiro_df = pd.read_sql_query(
        """
        SELECT
            tipo,
            descricao,
            categoria,
            valor,
            forma_pagamento,
            data,
            observacao
        FROM financeiro
        WHERE data = ?
        ORDER BY id DESC
        """,
        conn,
        params=(
            str(data_caixa),
        )
    )

    conn.close()

    total_entradas = 0.0
    total_saidas = 0.0

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

    return (
        financeiro_df,
        total_entradas,
        total_saidas
    )


# ==================================================
# PREPARAR TABELA
# ==================================================
def preparar_tabela_movimentos(financeiro_df):

    if financeiro_df.empty:

        return financeiro_df

    tabela = financeiro_df.copy()

    tabela["Valor"] = tabela[
        "valor"
    ].apply(
        formatar_moeda
    )

    tabela = tabela.rename(
        columns={
            "tipo": "Tipo",
            "descricao": "Descrição",
            "categoria": "Categoria",
            "forma_pagamento": "Pagamento",
            "observacao": "Observações"
        }
    )

    return tabela[
        [
            "Tipo",
            "Descrição",
            "Categoria",
            "Valor",
            "Pagamento",
            "Observações"
        ]
    ]


# ==================================================
# PÁGINA CAIXA DIÁRIO
# ==================================================
def mostrar_caixa():

    criar_tabela_caixa()

    st.title(
        "💰 Caixa Diário"
    )

    st.caption(
        "Abra o caixa, acompanhe as entradas e saídas "
        "e faça o fechamento no fim do expediente."
    )

    aba1, aba2, aba3 = st.tabs(
        [
            "💰 Caixa Atual",
            "📋 Movimentos do Dia",
            "📚 Histórico de Caixas"
        ]
    )

    # ==================================================
    # CAIXA ATUAL
    # ==================================================
    with aba1:

        caixa_aberto_df = buscar_caixa_aberto()

        if caixa_aberto_df.empty:

            st.subheader(
                "🔓 Abrir Caixa"
            )

            data_abertura = st.date_input(
                "Data do caixa",
                value=date.today(),
                format="DD/MM/YYYY",
                key="caixa_data_abertura"
            )

            responsavel_abertura = st.text_input(
                "Responsável pela abertura",
                key="caixa_responsavel_abertura"
            )

            valor_inicial = st.number_input(
                "Valor inicial em dinheiro (R$)",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                key="caixa_valor_inicial"
            )

            observacao_abertura = st.text_area(
                "Observações da abertura",
                placeholder=(
                    "Exemplo: Caixa iniciado com troco."
                ),
                key="caixa_observacao_abertura"
            )

            st.info(
                f"💵 Valor inicial: "
                f"{formatar_moeda(valor_inicial)}"
            )

            if st.button(
                "🔓 Abrir Caixa",
                use_container_width=True,
                key="btn_abrir_caixa"
            ):

                if responsavel_abertura.strip() == "":

                    st.error(
                        "Digite o nome do responsável."
                    )

                else:

                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT INTO caixa_diario
                        (
                            data,
                            valor_inicial,
                            responsavel_abertura,
                            hora_abertura,
                            observacao_abertura,
                            status
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            str(data_abertura),
                            float(valor_inicial),
                            responsavel_abertura.strip(),
                            datetime.now().strftime(
                                "%H:%M:%S"
                            ),
                            observacao_abertura.strip(),
                            "Aberto"
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "Caixa aberto com sucesso!"
                    )

                    st.rerun()

        else:

            caixa = caixa_aberto_df.iloc[0]

            data_caixa = str(
                caixa["data"]
            )

            (
                financeiro_df,
                total_entradas,
                total_saidas
            ) = calcular_movimentos(
                data_caixa
            )

            valor_inicial = float(
                caixa["valor_inicial"] or 0
            )

            saldo_esperado = (
                valor_inicial
                + total_entradas
                - total_saidas
            )

            st.success(
                "🟢 Caixa aberto"
            )

            st.write(
                f"📅 **Data:** "
                f"{formatar_data_br(data_caixa)}"
            )

            st.write(
                f"👤 **Responsável:** "
                f"{caixa['responsavel_abertura']}"
            )

            st.write(
                f"🕒 **Hora da abertura:** "
                f"{caixa['hora_abertura']}"
            )

            st.markdown("---")

            coluna1, coluna2, coluna3, coluna4 = (
                st.columns(4)
            )

            coluna1.metric(
                "💵 Valor inicial",
                formatar_moeda(
                    valor_inicial
                )
            )

            coluna2.metric(
                "➕ Entradas",
                formatar_moeda(
                    total_entradas
                )
            )

            coluna3.metric(
                "➖ Saídas",
                formatar_moeda(
                    total_saidas
                )
            )

            coluna4.metric(
                "🏦 Saldo esperado",
                formatar_moeda(
                    saldo_esperado
                )
            )

            st.markdown("---")

            st.subheader(
                "🔒 Fechar Caixa"
            )

            responsavel_fechamento = st.text_input(
                "Responsável pelo fechamento",
                value=str(
                    caixa[
                        "responsavel_abertura"
                    ] or ""
                ),
                key="caixa_responsavel_fechamento"
            )

            valor_contado = st.number_input(
                "Valor contado no caixa (R$)",
                min_value=0.0,
                value=float(
                    saldo_esperado
                ),
                step=10.0,
                format="%.2f",
                key="caixa_valor_contado"
            )

            diferenca = (
                float(valor_contado)
                - float(saldo_esperado)
            )

            observacao_fechamento = st.text_area(
                "Observações do fechamento",
                placeholder=(
                    "Informe qualquer diferença "
                    "ou observação importante."
                ),
                key="caixa_observacao_fechamento"
            )

            coluna_resultado1, coluna_resultado2 = (
                st.columns(2)
            )

            coluna_resultado1.metric(
                "🏦 Saldo esperado",
                formatar_moeda(
                    saldo_esperado
                )
            )

            coluna_resultado2.metric(
                "⚖️ Diferença",
                formatar_moeda(
                    diferenca
                )
            )

            if diferenca == 0:

                st.success(
                    "✅ O caixa está conferindo."
                )

            elif diferenca > 0:

                st.warning(
                    f"Existe uma sobra de "
                    f"{formatar_moeda(diferenca)}."
                )

            else:

                st.error(
                    f"Existe uma falta de "
                    f"{formatar_moeda(abs(diferenca))}."
                )

            confirmar_fechamento = st.checkbox(
                "Confirmo o fechamento deste caixa",
                key="confirmar_fechamento_caixa"
            )

            if st.button(
                "🔒 Fechar Caixa",
                use_container_width=True,
                key="btn_fechar_caixa"
            ):

                if responsavel_fechamento.strip() == "":

                    st.error(
                        "Digite o responsável "
                        "pelo fechamento."
                    )

                elif not confirmar_fechamento:

                    st.error(
                        "Marque a confirmação "
                        "antes de fechar."
                    )

                else:

                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        UPDATE caixa_diario
                        SET
                            total_entradas = ?,
                            total_saidas = ?,
                            saldo_esperado = ?,
                            valor_contado = ?,
                            diferenca = ?,
                            responsavel_fechamento = ?,
                            hora_fechamento = ?,
                            observacao_fechamento = ?,
                            status = 'Fechado'
                        WHERE id = ?
                        """,
                        (
                            float(total_entradas),
                            float(total_saidas),
                            float(saldo_esperado),
                            float(valor_contado),
                            float(diferenca),
                            responsavel_fechamento.strip(),
                            datetime.now().strftime(
                                "%H:%M:%S"
                            ),
                            observacao_fechamento.strip(),
                            int(caixa["id"])
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "Caixa fechado com sucesso!"
                    )

                    st.rerun()

    # ==================================================
    # MOVIMENTOS DO DIA
    # ==================================================
    with aba2:

        st.subheader(
            "📋 Movimentos do Caixa"
        )

        caixa_aberto_df = buscar_caixa_aberto()

        if caixa_aberto_df.empty:

            data_consulta = st.date_input(
                "Escolha a data",
                value=date.today(),
                format="DD/MM/YYYY",
                key="caixa_data_consulta"
            )

        else:

            data_consulta = str(
                caixa_aberto_df.iloc[0][
                    "data"
                ]
            )

            st.write(
                f"📅 Movimentos do caixa de "
                f"**{formatar_data_br(data_consulta)}**"
            )

        (
            financeiro_df,
            total_entradas,
            total_saidas
        ) = calcular_movimentos(
            data_consulta
        )

        coluna1, coluna2, coluna3 = st.columns(
            3
        )

        coluna1.metric(
            "➕ Entradas",
            formatar_moeda(
                total_entradas
            )
        )

        coluna2.metric(
            "➖ Saídas",
            formatar_moeda(
                total_saidas
            )
        )

        coluna3.metric(
            "📈 Resultado",
            formatar_moeda(
                total_entradas
                - total_saidas
            )
        )

        if financeiro_df.empty:

            st.info(
                "Não existem movimentos nesta data."
            )

        else:

            filtro_pagamento = st.selectbox(
                "Filtrar por forma de pagamento",
                [
                    "Todos"
                ] + FORMAS_PAGAMENTO,
                key="caixa_filtro_pagamento"
            )

            resultado_df = financeiro_df.copy()

            if filtro_pagamento != "Todos":

                resultado_df = resultado_df[
                    resultado_df[
                        "forma_pagamento"
                    ] == filtro_pagamento
                ]

            st.dataframe(
                preparar_tabela_movimentos(
                    resultado_df
                ),
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")

            st.subheader(
                "💳 Entradas por Forma de Pagamento"
            )

            entradas_df = financeiro_df[
                financeiro_df["tipo"]
                == "Entrada"
            ]

            if entradas_df.empty:

                st.info(
                    "Não existem entradas nesta data."
                )

            else:

                entradas_pagamento = (
                    entradas_df
                    .groupby(
                        "forma_pagamento"
                    )["valor"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                )

                st.bar_chart(
                    entradas_pagamento
                )

    # ==================================================
    # HISTÓRICO
    # ==================================================
    with aba3:

        st.subheader(
            "📚 Histórico de Caixas"
        )

        historico_df = carregar_historico_caixa()

        if historico_df.empty:

            st.info(
                "Ainda não existem caixas registrados."
            )

        else:

            tabela = historico_df.copy()

            tabela["Data"] = tabela[
                "data"
            ].apply(
                formatar_data_br
            )

            tabela["Valor Inicial"] = tabela[
                "valor_inicial"
            ].apply(
                formatar_moeda
            )

            tabela["Entradas"] = tabela[
                "total_entradas"
            ].apply(
                formatar_moeda
            )

            tabela["Saídas"] = tabela[
                "total_saidas"
            ].apply(
                formatar_moeda
            )

            tabela["Saldo Esperado"] = tabela[
                "saldo_esperado"
            ].apply(
                formatar_moeda
            )

            tabela["Valor Contado"] = tabela[
                "valor_contado"
            ].fillna(0).apply(
                formatar_moeda
            )

            tabela["Diferença"] = tabela[
                "diferenca"
            ].fillna(0).apply(
                formatar_moeda
            )

            tabela = tabela.rename(
                columns={
                    "status": "Status",
                    "responsavel_abertura":
                        "Responsável pela Abertura",
                    "responsavel_fechamento":
                        "Responsável pelo Fechamento"
                }
            )

            st.dataframe(
                tabela[
                    [
                        "Data",
                        "Status",
                        "Valor Inicial",
                        "Entradas",
                        "Saídas",
                        "Saldo Esperado",
                        "Valor Contado",
                        "Diferença",
                        "Responsável pela Abertura",
                        "Responsável pelo Fechamento"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

    st.markdown("---")

    st.caption(
        "BeautyFlow CRM • "
        "Desenvolvido por "
        "Luciana Oliveira de Albuquerque"
    )
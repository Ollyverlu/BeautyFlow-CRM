
from datetime import date, datetime

import pandas as pd
import streamlit as st

from banco import conectar


CATEGORIAS = [
    "Venda de Produto",
    "Serviço Realizado",
    "Compra de Material",
    "Conta de Água",
    "Conta de Luz",
    "Aluguel",
    "Transporte",
    "Manutenção",
    "Marketing",
    "Outro"
]


FORMAS_PAGAMENTO = [
    "Pix",
    "Dinheiro",
    "Cartão de Débito",
    "Cartão de Crédito",
    "Transferência",
    "Outro"
]


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================
def carregar_movimentos():

    conn = conectar()

    financeiro_df = pd.read_sql_query(
        """
        SELECT *
        FROM financeiro
        ORDER BY data DESC, id DESC
        """,
        conn
    )

    conn.close()

    return financeiro_df


def formatar_moeda(valor):

    valor_formatado = f"{float(valor):,.2f}"

    valor_formatado = (
        valor_formatado
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {valor_formatado}"


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


def calcular_totais(financeiro_df):

    total_entradas = 0.0
    total_saidas = 0.0

    if financeiro_df.empty:

        return (
            total_entradas,
            total_saidas,
            0.0
        )

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

    saldo = (
        total_entradas
        - total_saidas
    )

    return (
        total_entradas,
        total_saidas,
        saldo
    )


def preparar_tabela(financeiro_df):

    if financeiro_df.empty:

        return financeiro_df

    tabela = financeiro_df.copy()

    tabela["Data"] = tabela["data"].apply(
        formatar_data_br
    )

    tabela["Tipo"] = tabela["tipo"]
    tabela["Descrição"] = tabela["descricao"]
    tabela["Categoria"] = tabela["categoria"]

    tabela["Valor"] = tabela["valor"].apply(
        formatar_moeda
    )

    tabela["Pagamento"] = tabela[
        "forma_pagamento"
    ]

    tabela["Observações"] = tabela[
        "observacao"
    ]

    return tabela[
        [
            "Data",
            "Tipo",
            "Descrição",
            "Categoria",
            "Valor",
            "Pagamento",
            "Observações"
        ]
    ]


# ==================================================
# PÁGINA FINANCEIRO
# ==================================================
def mostrar_financeiro():

    st.title("💰 Financeiro BeautyFlow")

    st.caption(
        "Controle entradas, saídas, saldo e "
        "formas de pagamento do seu negócio."
    )

    aba1, aba2, aba3, aba4 = st.tabs(
        [
            "➕ Registrar Movimento",
            "📋 Histórico",
            "📊 Painel Financeiro",
            "🗑️ Excluir Movimento"
        ]
    )

    # ==================================================
    # REGISTRAR MOVIMENTO
    # ==================================================
    with aba1:

        st.subheader(
            "➕ Registrar Entrada ou Saída"
        )

        coluna1, coluna2 = st.columns(2)

        with coluna1:

            tipo = st.selectbox(
                "Tipo de movimento",
                [
                    "Entrada",
                    "Saída"
                ],
                key="financeiro_tipo"
            )

            descricao = st.text_input(
                "Descrição",
                placeholder=(
                    "Exemplo: Serviço de balayagem"
                ),
                key="financeiro_descricao"
            )

            categoria = st.selectbox(
                "Categoria",
                CATEGORIAS,
                key="financeiro_categoria"
            )

        with coluna2:

            valor = st.number_input(
                "Valor (R$)",
                min_value=0.0,
                format="%.2f",
                key="financeiro_valor"
            )

            forma_pagamento = st.selectbox(
                "Forma de pagamento",
                FORMAS_PAGAMENTO,
                key="financeiro_pagamento"
            )

            data_movimento = st.date_input(
                "Data",
                value=date.today(),
                format="DD/MM/YYYY",
                key="financeiro_data"
            )

        observacao = st.text_area(
            "Observações",
            placeholder=(
                "Informações adicionais sobre "
                "este movimento financeiro."
            ),
            key="financeiro_observacao"
        )

        if tipo == "Entrada":

            st.success(
                f"💵 Entrada: "
                f"{formatar_moeda(valor)}"
            )

        else:

            st.warning(
                f"💸 Saída: "
                f"{formatar_moeda(valor)}"
            )

        if st.button(
            "💾 Salvar Movimento",
            key="btn_salvar_movimento",
            use_container_width=True
        ):

            if descricao.strip() == "":

                st.error(
                    "Digite uma descrição."
                )

            elif valor <= 0:

                st.error(
                    "O valor deve ser maior que zero."
                )

            else:

                conn = conectar()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO financeiro
                    (
                        tipo,
                        descricao,
                        categoria,
                        valor,
                        forma_pagamento,
                        data,
                        observacao
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tipo,
                        descricao.strip(),
                        categoria,
                        float(valor),
                        forma_pagamento,
                        str(data_movimento),
                        observacao.strip()
                    )
                )

                conn.commit()
                conn.close()

                st.success(
                    "Movimento financeiro salvo "
                    "com sucesso!"
                )

                st.rerun()

    # ==================================================
    # HISTÓRICO
    # ==================================================
    with aba2:

        st.subheader(
            "📋 Histórico Financeiro"
        )

        financeiro_df = carregar_movimentos()

        if financeiro_df.empty:

            st.info(
                "Ainda não existem movimentos "
                "financeiros registrados."
            )

        else:

            coluna_data1, coluna_data2 = st.columns(2)

            datas_convertidas = pd.to_datetime(
                financeiro_df["data"],
                errors="coerce"
            )

            data_minima = datas_convertidas.min()
            data_maxima = datas_convertidas.max()

            if pd.isna(data_minima):

                data_minima = pd.Timestamp(
                    date.today()
                )

            if pd.isna(data_maxima):

                data_maxima = pd.Timestamp(
                    date.today()
                )

            with coluna_data1:

                data_inicial = st.date_input(
                    "Data inicial",
                    value=data_minima.date(),
                    format="DD/MM/YYYY",
                    key="historico_data_inicial"
                )

            with coluna_data2:

                data_final = st.date_input(
                    "Data final",
                    value=data_maxima.date(),
                    format="DD/MM/YYYY",
                    key="historico_data_final"
                )

            if data_inicial > data_final:

                st.error(
                    "A data inicial não pode ser "
                    "maior que a data final."
                )

            else:

                tipo_filtro = st.selectbox(
                    "Filtrar por tipo",
                    [
                        "Todos",
                        "Entrada",
                        "Saída"
                    ],
                    key="historico_tipo"
                )

                busca = st.text_input(
                    "Pesquisar por descrição ou categoria",
                    key="historico_busca"
                )

                resultado_df = financeiro_df.copy()

                resultado_df["data_convertida"] = (
                    pd.to_datetime(
                        resultado_df["data"],
                        errors="coerce"
                    )
                )

                resultado_df = resultado_df[
                    (
                        resultado_df[
                            "data_convertida"
                        ].dt.date
                        >= data_inicial
                    )
                    &
                    (
                        resultado_df[
                            "data_convertida"
                        ].dt.date
                        <= data_final
                    )
                ]

                if tipo_filtro != "Todos":

                    resultado_df = resultado_df[
                        resultado_df["tipo"]
                        == tipo_filtro
                    ]

                if busca.strip() != "":

                    busca_normalizada = (
                        busca
                        .strip()
                        .lower()
                    )

                    filtro_descricao = (
                        resultado_df["descricao"]
                        .fillna("")
                        .astype(str)
                        .str.lower()
                        .str.contains(
                            busca_normalizada,
                            regex=False
                        )
                    )

                    filtro_categoria = (
                        resultado_df["categoria"]
                        .fillna("")
                        .astype(str)
                        .str.lower()
                        .str.contains(
                            busca_normalizada,
                            regex=False
                        )
                    )

                    resultado_df = resultado_df[
                        filtro_descricao
                        | filtro_categoria
                    ]

                total_entradas, total_saidas, saldo = (
                    calcular_totais(
                        resultado_df
                    )
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "💵 Entradas do período",
                    formatar_moeda(
                        total_entradas
                    )
                )

                col2.metric(
                    "💸 Saídas do período",
                    formatar_moeda(
                        total_saidas
                    )
                )

                col3.metric(
                    "📈 Saldo do período",
                    formatar_moeda(
                        saldo
                    )
                )

                st.write(
                    f"**Movimentos encontrados:** "
                    f"{len(resultado_df)}"
                )

                if resultado_df.empty:

                    st.warning(
                        "Nenhum movimento encontrado "
                        "com estes filtros."
                    )

                else:

                    st.dataframe(
                        preparar_tabela(
                            resultado_df
                        ),
                        use_container_width=True,
                        hide_index=True
                    )

    # ==================================================
    # PAINEL FINANCEIRO
    # ==================================================
    with aba3:

        st.subheader(
            "📊 Painel Financeiro"
        )

        financeiro_df = carregar_movimentos()

        hoje = str(
            date.today()
        )

        mes_atual = date.today().strftime(
            "%Y-%m"
        )

        financeiro_hoje = financeiro_df[
            financeiro_df["data"].astype(str)
            == hoje
        ].copy()

        financeiro_mes = financeiro_df[
            financeiro_df["data"]
            .astype(str)
            .str.startswith(
                mes_atual
            )
        ].copy()

        (
            entradas_total,
            saidas_total,
            saldo_total
        ) = calcular_totais(
            financeiro_df
        )

        (
            entradas_hoje,
            saidas_hoje,
            saldo_hoje
        ) = calcular_totais(
            financeiro_hoje
        )

        (
            entradas_mes,
            saidas_mes,
            saldo_mes
        ) = calcular_totais(
            financeiro_mes
        )

        st.subheader(
            "🌸 Resumo de Hoje"
        )

        coluna1, coluna2, coluna3 = st.columns(3)

        coluna1.metric(
            "💵 Entradas hoje",
            formatar_moeda(
                entradas_hoje
            )
        )

        coluna2.metric(
            "💸 Saídas hoje",
            formatar_moeda(
                saidas_hoje
            )
        )

        coluna3.metric(
            "📈 Saldo hoje",
            formatar_moeda(
                saldo_hoje
            )
        )

        st.markdown("---")

        st.subheader(
            "📅 Resumo do Mês"
        )

        coluna4, coluna5, coluna6 = st.columns(3)

        coluna4.metric(
            "💵 Entradas no mês",
            formatar_moeda(
                entradas_mes
            )
        )

        coluna5.metric(
            "💸 Saídas no mês",
            formatar_moeda(
                saidas_mes
            )
        )

        coluna6.metric(
            "📈 Saldo do mês",
            formatar_moeda(
                saldo_mes
            )
        )

        st.markdown("---")

        st.subheader(
            "🏦 Resumo Geral"
        )

        coluna7, coluna8, coluna9 = st.columns(3)

        coluna7.metric(
            "💵 Total de entradas",
            formatar_moeda(
                entradas_total
            )
        )

        coluna8.metric(
            "💸 Total de saídas",
            formatar_moeda(
                saidas_total
            )
        )

        coluna9.metric(
            "📈 Saldo atual",
            formatar_moeda(
                saldo_total
            )
        )

        st.markdown("---")

        if financeiro_df.empty:

            st.info(
                "Ainda não existem dados "
                "para gerar gráficos."
            )

        else:

            coluna_grafico1, coluna_grafico2 = (
                st.columns(2)
            )

            with coluna_grafico1:

                st.subheader(
                    "📈 Movimentação por Data"
                )

                movimentos_por_data = (
                    financeiro_df
                    .assign(
                        valor_com_sinal=lambda tabela: (
                            tabela.apply(
                                lambda linha: (
                                    linha["valor"]
                                    if linha["tipo"]
                                    == "Entrada"
                                    else -linha["valor"]
                                ),
                                axis=1
                            )
                        )
                    )
                    .groupby(
                        "data"
                    )["valor_com_sinal"]
                    .sum()
                    .sort_index()
                )

                st.bar_chart(
                    movimentos_por_data
                )

            with coluna_grafico2:

                st.subheader(
                    "💳 Formas de Pagamento"
                )

                pagamentos_df = (
                    financeiro_df
                    .groupby(
                        "forma_pagamento"
                    )["valor"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                )

                st.bar_chart(
                    pagamentos_df
                )

            st.markdown("---")

            st.subheader(
                "📂 Gastos por Categoria"
            )

            saidas_categorias = financeiro_df[
                financeiro_df["tipo"]
                == "Saída"
            ]

            if saidas_categorias.empty:

                st.info(
                    "Ainda não existem saídas "
                    "para mostrar por categoria."
                )

            else:

                gastos_categoria = (
                    saidas_categorias
                    .groupby(
                        "categoria"
                    )["valor"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                )

                st.bar_chart(
                    gastos_categoria
                )

    # ==================================================
    # EXCLUIR MOVIMENTO
    # ==================================================
    with aba4:

        st.subheader(
            "🗑️ Excluir Movimento Financeiro"
        )

        financeiro_df = carregar_movimentos()

        if financeiro_df.empty:

            st.info(
                "Ainda não existem movimentos "
                "para excluir."
            )

        else:

            financeiro_df["opcao"] = (
                financeiro_df["id"]
                .astype(str)
                + " - "
                + financeiro_df["tipo"]
                + " - "
                + financeiro_df["descricao"]
                + " - "
                + financeiro_df["data"]
                .apply(formatar_data_br)
                + " - "
                + financeiro_df["valor"]
                .apply(formatar_moeda)
            )

            movimento_escolhido = st.selectbox(
                "Escolha o movimento",
                financeiro_df["opcao"].tolist(),
                key="excluir_movimento"
            )

            movimento_id = int(
                movimento_escolhido
                .split(" - ")[0]
            )

            movimento = financeiro_df[
                financeiro_df["id"]
                == movimento_id
            ].iloc[0]

            st.warning(
                f"Você está prestes a excluir: "
                f"{movimento['descricao']} — "
                f"{formatar_moeda(movimento['valor'])}"
            )

            confirmar = st.checkbox(
                "Confirmo que desejo excluir "
                "este movimento financeiro",
                key="confirmar_exclusao_financeiro"
            )

            if st.button(
                "🗑️ Excluir Movimento",
                key="btn_excluir_financeiro",
                use_container_width=True
            ):

                if not confirmar:

                    st.error(
                        "Marque a confirmação "
                        "antes de excluir."
                    )

                else:

                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        DELETE FROM financeiro
                        WHERE id = ?
                        """,
                        (movimento_id,)
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "Movimento excluído "
                        "com sucesso!"
                    )

                    st.rerun()

    # ==================================================
    # ÚLTIMOS MOVIMENTOS
    # ==================================================
    st.markdown("---")

    st.subheader(
        "🧾 Últimos Movimentos"
    )

    ultimos_movimentos = carregar_movimentos()

    if ultimos_movimentos.empty:

        st.info(
            "Ainda não existem movimentos "
            "financeiros registrados."
        )

    else:

        st.dataframe(
            preparar_tabela(
                ultimos_movimentos.head(10)
            ),
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "BeautyFlow CRM • "
        "Desenvolvido por Luciana Ollyver"
    )
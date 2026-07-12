
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from banco import conectar

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)


# ==================================================
# CAMINHOS DO PROJETO
# ==================================================
PASTA_PROJETO = Path(__file__).resolve().parent.parent

CAMINHO_LOGO = (
    PASTA_PROJETO
    / "assets"
    / "imagens"
    / "logo_beautyflow.png"
)


# ==================================================
# CORES DO BEAUTYFLOW
# ==================================================
ROSA_PRINCIPAL = colors.HexColor("#B85A6B")
ROSA_CLARO = colors.HexColor("#FCE7EF")
DOURADO = colors.HexColor("#D4AF37")
CINZA_CLARO = colors.HexColor("#F5F5F5")
GRAFITE = colors.HexColor("#333333")
BRANCO = colors.white


# ==================================================
# FUNÇÕES AUXILIARES
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


def formatar_horario(valor):

    texto = str(valor)

    for formato in [
        "%H:%M:%S",
        "%H:%M"
    ]:

        try:

            horario_convertido = datetime.strptime(
                texto,
                formato
            )

            return horario_convertido.strftime(
                "%H:%M"
            )

        except ValueError:
            continue

    return texto


def calcular_totais_financeiros(financeiro_df):

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


# ==================================================
# PREPARAR EXCEL
# ==================================================
def preparar_vendas_excel(vendas_df):

    if vendas_df.empty:
        return vendas_df

    tabela = vendas_df.copy()

    tabela["data"] = tabela["data"].apply(
        formatar_data_br
    )

    tabela = tabela.rename(
        columns={
            "id": "ID",
            "produto": "Produto",
            "quantidade": "Quantidade",
            "valor_unitario": "Valor Unitário",
            "valor_total": "Valor Total",
            "cliente": "Cliente",
            "data": "Data"
        }
    )

    return tabela


def preparar_financeiro_excel(financeiro_df):

    if financeiro_df.empty:
        return financeiro_df

    tabela = financeiro_df.copy()

    tabela["data"] = tabela["data"].apply(
        formatar_data_br
    )

    tabela = tabela.rename(
        columns={
            "id": "ID",
            "tipo": "Tipo",
            "descricao": "Descrição",
            "categoria": "Categoria",
            "valor": "Valor",
            "forma_pagamento": "Forma de Pagamento",
            "data": "Data",
            "observacao": "Observações"
        }
    )

    return tabela


def criar_excel(
    vendas_df,
    financeiro_df,
    agendamentos_df,
    resumo_df,
    rankings_df
):

    arquivo = BytesIO()

    with pd.ExcelWriter(
        arquivo,
        engine="openpyxl"
    ) as writer:

        resumo_df.to_excel(
            writer,
            sheet_name="Resumo Executivo",
            index=False
        )

        preparar_vendas_excel(
            vendas_df
        ).to_excel(
            writer,
            sheet_name="Vendas",
            index=False
        )

        preparar_financeiro_excel(
            financeiro_df
        ).to_excel(
            writer,
            sheet_name="Financeiro",
            index=False
        )

        agendamentos_df.to_excel(
            writer,
            sheet_name="Agendamentos",
            index=False
        )

        rankings_df.to_excel(
            writer,
            sheet_name="Rankings",
            index=False
        )

    arquivo.seek(0)

    return arquivo


# ==================================================
# FUNÇÕES DO PDF
# ==================================================
def texto_pdf(valor, estilo):

    if valor is None:
        valor = ""

    return Paragraph(
        str(valor),
        estilo
    )


def adicionar_rodape_pdf(canvas, documento):

    canvas.saveState()

    largura, altura = landscape(A4)

    canvas.setStrokeColor(
        ROSA_PRINCIPAL
    )

    canvas.line(
        1.2 * cm,
        1.1 * cm,
        largura - 1.2 * cm,
        1.1 * cm
    )

    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.setFillColor(
        GRAFITE
    )

    canvas.drawString(
        1.2 * cm,
        0.65 * cm,
        "BeautyFlow CRM - Desenvolvido por "
        "Luciana Oliveira de Albuquerque"
    )

    canvas.drawRightString(
        largura - 1.2 * cm,
        0.65 * cm,
        f"Página {documento.page}"
    )

    canvas.restoreState()


def criar_tabela_pdf(
    dados,
    larguras=None,
    repetir_cabecalho=True
):

    tabela = Table(
        dados,
        colWidths=larguras,
        repeatRows=1 if repetir_cabecalho else 0
    )

    tabela.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    ROSA_PRINCIPAL
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    BRANCO
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, 0),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#D9A9B6")
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        BRANCO,
                        ROSA_CLARO
                    ]
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                )
            ]
        )
    )

    return tabela


def criar_pdf(
    data_inicial,
    data_final,
    clientes_total,
    total_atendimentos,
    total_vendas,
    itens_vendidos,
    ticket_medio,
    total_entradas,
    total_saidas,
    saldo,
    servico_campeao,
    cliente_vip,
    produto_campeao,
    pagamento_campeao,
    vendas_df,
    financeiro_df,
    agendamentos_df
):

    arquivo = BytesIO()

    documento = SimpleDocTemplate(
        arquivo,
        pagesize=landscape(A4),
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.6 * cm,
        title="Relatório Executivo BeautyFlow CRM",
        author="Luciana Oliveira de Albuquerque"
    )

    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "TituloBeautyFlow",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        textColor=ROSA_PRINCIPAL,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    estilo_subtitulo = ParagraphStyle(
        "SubtituloBeautyFlow",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=GRAFITE,
        alignment=TA_CENTER,
        spaceAfter=12
    )

    estilo_secao = ParagraphStyle(
        "SecaoBeautyFlow",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=ROSA_PRINCIPAL,
        spaceBefore=8,
        spaceAfter=8
    )

    estilo_celula = ParagraphStyle(
        "CelulaBeautyFlow",
        parent=estilos["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=GRAFITE
    )

    elementos = []

    # ==================================================
    # CABEÇALHO
    # ==================================================
    if CAMINHO_LOGO.exists():

        try:

            logo = Image(
                str(CAMINHO_LOGO),
                width=4.5 * cm,
                height=2.5 * cm
            )

            logo.hAlign = "CENTER"

            elementos.append(
                logo
            )

            elementos.append(
                Spacer(
                    1,
                    0.2 * cm
                )
            )

        except Exception:

            pass

    elementos.append(
        Paragraph(
            "BeautyFlow CRM",
            estilo_titulo
        )
    )

    elementos.append(
        Paragraph(
            "Relatório Executivo - "
            "Onde a beleza encontra a organização",
            estilo_subtitulo
        )
    )

    elementos.append(
        Paragraph(
            (
                f"Período: "
                f"{data_inicial.strftime('%d/%m/%Y')} "
                f"até "
                f"{data_final.strftime('%d/%m/%Y')}"
            ),
            estilo_subtitulo
        )
    )

    elementos.append(
        Spacer(
            1,
            0.3 * cm
        )
    )

    # ==================================================
    # RESUMO EXECUTIVO
    # ==================================================
    elementos.append(
        Paragraph(
            "Resumo Executivo",
            estilo_secao
        )
    )

    dados_resumo = [
        [
            "Indicador",
            "Resultado",
            "Indicador",
            "Resultado"
        ],
        [
            "Clientes cadastradas",
            str(int(clientes_total)),
            "Atendimentos",
            str(int(total_atendimentos))
        ],
        [
            "Total em vendas",
            formatar_moeda(total_vendas),
            "Itens vendidos",
            str(int(itens_vendidos))
        ],
        [
            "Ticket médio",
            formatar_moeda(ticket_medio),
            "Entradas",
            formatar_moeda(total_entradas)
        ],
        [
            "Saídas",
            formatar_moeda(total_saidas),
            "Saldo",
            formatar_moeda(saldo)
        ]
    ]

    elementos.append(
        criar_tabela_pdf(
            dados_resumo,
            larguras=[
                6.3 * cm,
                5.2 * cm,
                6.3 * cm,
                5.2 * cm
            ]
        )
    )

    elementos.append(
        Spacer(
            1,
            0.5 * cm
        )
    )

    # ==================================================
    # DESTAQUES
    # ==================================================
    elementos.append(
        Paragraph(
            "Destaques do Período",
            estilo_secao
        )
    )

    dados_destaques = [
        [
            "Categoria",
            "Resultado"
        ],
        [
            "Serviço campeão",
            servico_campeao
        ],
        [
            "Cliente VIP",
            cliente_vip
        ],
        [
            "Produto campeão",
            produto_campeao
        ],
        [
            "Forma de pagamento principal",
            pagamento_campeao
        ]
    ]

    elementos.append(
        criar_tabela_pdf(
            dados_destaques,
            larguras=[
                10 * cm,
                13 * cm
            ]
        )
    )

    # ==================================================
    # VENDAS
    # ==================================================
    elementos.append(
        PageBreak()
    )

    elementos.append(
        Paragraph(
            "Vendas do Período",
            estilo_secao
        )
    )

    if vendas_df.empty:

        elementos.append(
            Paragraph(
                "Não existem vendas no período selecionado.",
                estilo_celula
            )
        )

    else:

        dados_vendas = [
            [
                "Data",
                "Cliente",
                "Produto",
                "Qtd.",
                "Valor unitário",
                "Valor total"
            ]
        ]

        for _, linha in vendas_df.iterrows():

            dados_vendas.append(
                [
                    texto_pdf(
                        formatar_data_br(
                            linha.get(
                                "data",
                                ""
                            )
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        linha.get(
                            "cliente",
                            ""
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        linha.get(
                            "produto",
                            ""
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        linha.get(
                            "quantidade",
                            ""
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        formatar_moeda(
                            linha.get(
                                "valor_unitario",
                                0
                            )
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        formatar_moeda(
                            linha.get(
                                "valor_total",
                                0
                            )
                        ),
                        estilo_celula
                    )
                ]
            )

        elementos.append(
            criar_tabela_pdf(
                dados_vendas,
                larguras=[
                    3 * cm,
                    5 * cm,
                    5.5 * cm,
                    1.8 * cm,
                    3.5 * cm,
                    3.5 * cm
                ]
            )
        )

    # ==================================================
    # FINANCEIRO
    # ==================================================
    elementos.append(
        PageBreak()
    )

    elementos.append(
        Paragraph(
            "Movimentos Financeiros",
            estilo_secao
        )
    )

    if financeiro_df.empty:

        elementos.append(
            Paragraph(
                "Não existem movimentos financeiros "
                "no período selecionado.",
                estilo_celula
            )
        )

    else:

        dados_financeiro = [
            [
                "Data",
                "Tipo",
                "Descrição",
                "Categoria",
                "Valor",
                "Pagamento"
            ]
        ]

        for _, linha in financeiro_df.iterrows():

            dados_financeiro.append(
                [
                    texto_pdf(
                        formatar_data_br(
                            linha.get(
                                "data",
                                ""
                            )
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        linha.get(
                            "tipo",
                            ""
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        linha.get(
                            "descricao",
                            ""
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        linha.get(
                            "categoria",
                            ""
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        formatar_moeda(
                            linha.get(
                                "valor",
                                0
                            )
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        linha.get(
                            "forma_pagamento",
                            ""
                        ),
                        estilo_celula
                    )
                ]
            )

        elementos.append(
            criar_tabela_pdf(
                dados_financeiro,
                larguras=[
                    2.8 * cm,
                    2.5 * cm,
                    6 * cm,
                    4.5 * cm,
                    3.2 * cm,
                    4.5 * cm
                ]
            )
        )

    # ==================================================
    # AGENDAMENTOS
    # ==================================================
    elementos.append(
        PageBreak()
    )

    elementos.append(
        Paragraph(
            "Agendamentos do Período",
            estilo_secao
        )
    )

    if agendamentos_df.empty:

        elementos.append(
            Paragraph(
                "Não existem agendamentos no período selecionado.",
                estilo_celula
            )
        )

    else:

        dados_agendamentos = [
            [
                "Data",
                "Horário",
                "Cliente",
                "Serviço"
            ]
        ]

        for _, linha in agendamentos_df.iterrows():

            dados_agendamentos.append(
                [
                    texto_pdf(
                        formatar_data_br(
                            linha.get(
                                "Data",
                                ""
                            )
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        formatar_horario(
                            linha.get(
                                "Horário",
                                ""
                            )
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        linha.get(
                            "Cliente",
                            ""
                        ),
                        estilo_celula
                    ),
                    texto_pdf(
                        linha.get(
                            "Serviço",
                            ""
                        ),
                        estilo_celula
                    )
                ]
            )

        elementos.append(
            criar_tabela_pdf(
                dados_agendamentos,
                larguras=[
                    4 * cm,
                    3 * cm,
                    7 * cm,
                    9 * cm
                ]
            )
        )

    documento.build(
        elementos,
        onFirstPage=adicionar_rodape_pdf,
        onLaterPages=adicionar_rodape_pdf
    )

    arquivo.seek(0)

    return arquivo


# ==================================================
# PÁGINA RELATÓRIOS
# ==================================================
def mostrar_relatorios():

    st.title(
        "📊 Relatórios Executivos"
    )

    st.caption(
        "Acompanhe os resultados do BeautyFlow CRM "
        "por período e exporte os dados em Excel e PDF."
    )

    st.markdown("---")

    coluna1, coluna2 = st.columns(2)

    with coluna1:

        data_inicial = st.date_input(
            "Data inicial",
            value=date.today().replace(
                day=1
            ),
            format="DD/MM/YYYY",
            key="relatorio_data_inicial"
        )

    with coluna2:

        data_final = st.date_input(
            "Data final",
            value=date.today(),
            format="DD/MM/YYYY",
            key="relatorio_data_final"
        )

    if data_inicial > data_final:

        st.error(
            "A data inicial não pode ser maior "
            "que a data final."
        )

        return

    conn = conectar()

    try:

        # ==================================================
        # CONSULTAS
        # ==================================================
        vendas_df = pd.read_sql_query(
            """
            SELECT *
            FROM vendas
            WHERE data BETWEEN ? AND ?
            ORDER BY data DESC, id DESC
            """,
            conn,
            params=(
                str(data_inicial),
                str(data_final)
            )
        )

        financeiro_df = pd.read_sql_query(
            """
            SELECT *
            FROM financeiro
            WHERE data BETWEEN ? AND ?
            ORDER BY data DESC, id DESC
            """,
            conn,
            params=(
                str(data_inicial),
                str(data_final)
            )
        )

        agendamentos_df = pd.read_sql_query(
            """
            SELECT
                id AS ID,
                cliente AS Cliente,
                data AS Data,
                horario AS Horário,
                servico AS Serviço
            FROM agendamentos
            WHERE data BETWEEN ? AND ?
            ORDER BY data DESC, horario DESC
            """,
            conn,
            params=(
                str(data_inicial),
                str(data_final)
            )
        )

        clientes_total = pd.read_sql_query(
            """
            SELECT COUNT(*) AS total
            FROM clientes
            """,
            conn
        )["total"][0]

        # ==================================================
        # CÁLCULOS
        # ==================================================
        total_vendas = 0.0
        itens_vendidos = 0
        quantidade_vendas = 0

        if not vendas_df.empty:

            total_vendas = float(
                vendas_df[
                    "valor_total"
                ].sum()
            )

            itens_vendidos = int(
                vendas_df[
                    "quantidade"
                ].sum()
            )

            quantidade_vendas = len(
                vendas_df
            )

        if quantidade_vendas > 0:

            ticket_medio = (
                total_vendas
                / quantidade_vendas
            )

        else:

            ticket_medio = 0.0

        (
            total_entradas,
            total_saidas,
            saldo
        ) = calcular_totais_financeiros(
            financeiro_df
        )

        total_atendimentos = len(
            agendamentos_df
        )

        # ==================================================
        # RANKINGS
        # ==================================================
        produto_campeao = "Sem dados"
        cliente_vip = "Sem dados"
        servico_campeao = "Sem dados"
        pagamento_campeao = "Sem dados"

        produtos_ranking = pd.DataFrame()
        clientes_ranking = pd.DataFrame()
        servicos_ranking = pd.DataFrame()
        pagamentos_ranking = pd.DataFrame()

        if not vendas_df.empty:

            produtos_ranking = (
                vendas_df
                .groupby(
                    "produto"
                )["quantidade"]
                .sum()
                .sort_values(
                    ascending=False
                )
                .reset_index()
            )

            if not produtos_ranking.empty:

                produto_campeao = str(
                    produtos_ranking.iloc[
                        0
                    ]["produto"]
                )

            clientes_validos = vendas_df[
                vendas_df["cliente"]
                .fillna("")
                .astype(str)
                .str.strip()
                != ""
            ]

            if not clientes_validos.empty:

                clientes_ranking = (
                    clientes_validos
                    .groupby(
                        "cliente"
                    )["valor_total"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                    .reset_index()
                )

                cliente_vip = str(
                    clientes_ranking.iloc[
                        0
                    ]["cliente"]
                )

        if not agendamentos_df.empty:

            servicos_ranking = (
                agendamentos_df
                .groupby(
                    "Serviço"
                )
                .size()
                .sort_values(
                    ascending=False
                )
                .reset_index(
                    name="Quantidade"
                )
            )

            if not servicos_ranking.empty:

                servico_campeao = str(
                    servicos_ranking.iloc[
                        0
                    ]["Serviço"]
                )

        if not financeiro_df.empty:

            pagamentos_validos = financeiro_df[
                financeiro_df[
                    "forma_pagamento"
                ]
                .fillna("")
                .astype(str)
                .str.strip()
                != ""
            ]

            if not pagamentos_validos.empty:

                pagamentos_ranking = (
                    pagamentos_validos
                    .groupby(
                        "forma_pagamento"
                    )["valor"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                    .reset_index()
                )

                pagamento_campeao = str(
                    pagamentos_ranking.iloc[
                        0
                    ]["forma_pagamento"]
                )

        # ==================================================
        # PAINEL EXECUTIVO
        # ==================================================
        st.subheader(
            "🌸 Resumo Executivo"
        )

        coluna3, coluna4, coluna5, coluna6 = st.columns(
            4
        )

        coluna3.metric(
            "👩‍💼 Clientes cadastradas",
            int(clientes_total)
        )

        coluna4.metric(
            "📅 Atendimentos",
            total_atendimentos
        )

        coluna5.metric(
            "💰 Total em vendas",
            formatar_moeda(
                total_vendas
            )
        )

        coluna6.metric(
            "📈 Saldo financeiro",
            formatar_moeda(
                saldo
            )
        )

        coluna7, coluna8, coluna9, coluna10 = st.columns(
            4
        )

        coluna7.metric(
            "📦 Itens vendidos",
            itens_vendidos
        )

        coluna8.metric(
            "🎯 Ticket médio",
            formatar_moeda(
                ticket_medio
            )
        )

        coluna9.metric(
            "💵 Entradas",
            formatar_moeda(
                total_entradas
            )
        )

        coluna10.metric(
            "💸 Saídas",
            formatar_moeda(
                total_saidas
            )
        )

        st.markdown("---")

        # ==================================================
        # DESTAQUES
        # ==================================================
        st.subheader(
            "🏆 Destaques do Período"
        )

        destaque1, destaque2, destaque3, destaque4 = st.columns(
            4
        )

        destaque1.metric(
            "🏆 Serviço campeão",
            servico_campeao
        )

        destaque2.metric(
            "⭐ Cliente VIP",
            cliente_vip
        )

        destaque3.metric(
            "📦 Produto campeão",
            produto_campeao
        )

        destaque4.metric(
            "💳 Pagamento principal",
            pagamento_campeao
        )

        st.markdown("---")

        # ==================================================
        # ABAS
        # ==================================================
        aba1, aba2, aba3, aba4 = st.tabs(
            [
                "💰 Vendas",
                "📋 Financeiro",
                "📅 Atendimentos",
                "🏆 Rankings"
            ]
        )

        with aba1:

            st.subheader(
                "💰 Vendas do Período"
            )

            if vendas_df.empty:

                st.info(
                    "Não existem vendas no período."
                )

            else:

                tabela_vendas = vendas_df.copy()

                tabela_vendas[
                    "data"
                ] = tabela_vendas[
                    "data"
                ].apply(
                    formatar_data_br
                )

                st.dataframe(
                    tabela_vendas,
                    use_container_width=True,
                    hide_index=True
                )

                st.subheader(
                    "📈 Faturamento por Data"
                )

                vendas_por_data = (
                    vendas_df
                    .groupby(
                        "data"
                    )["valor_total"]
                    .sum()
                    .sort_index()
                )

                st.bar_chart(
                    vendas_por_data
                )

        with aba2:

            st.subheader(
                "📋 Movimentos Financeiros"
            )

            if financeiro_df.empty:

                st.info(
                    "Não existem movimentos financeiros "
                    "no período."
                )

            else:

                tabela_financeiro = financeiro_df.copy()

                tabela_financeiro[
                    "data"
                ] = tabela_financeiro[
                    "data"
                ].apply(
                    formatar_data_br
                )

                st.dataframe(
                    tabela_financeiro,
                    use_container_width=True,
                    hide_index=True
                )

                resumo_tipo = (
                    financeiro_df
                    .groupby(
                        "tipo"
                    )["valor"]
                    .sum()
                )

                st.subheader(
                    "📊 Entradas e Saídas"
                )

                st.bar_chart(
                    resumo_tipo
                )

        with aba3:

            st.subheader(
                "📅 Atendimentos do Período"
            )

            if agendamentos_df.empty:

                st.info(
                    "Não existem atendimentos no período."
                )

            else:

                tabela_agenda = agendamentos_df.copy()

                tabela_agenda[
                    "Data"
                ] = tabela_agenda[
                    "Data"
                ].apply(
                    formatar_data_br
                )

                tabela_agenda[
                    "Horário"
                ] = tabela_agenda[
                    "Horário"
                ].apply(
                    formatar_horario
                )

                st.dataframe(
                    tabela_agenda,
                    use_container_width=True,
                    hide_index=True
                )

        with aba4:

            st.subheader(
                "🏆 Ranking de Produtos"
            )

            if produtos_ranking.empty:

                st.info(
                    "Ainda não existem produtos vendidos."
                )

            else:

                st.dataframe(
                    produtos_ranking,
                    use_container_width=True,
                    hide_index=True
                )

            st.subheader(
                "⭐ Ranking de Clientes"
            )

            if clientes_ranking.empty:

                st.info(
                    "Ainda não existem vendas "
                    "vinculadas às clientes."
                )

            else:

                ranking_clientes = clientes_ranking.copy()

                ranking_clientes[
                    "valor_total"
                ] = ranking_clientes[
                    "valor_total"
                ].apply(
                    formatar_moeda
                )

                st.dataframe(
                    ranking_clientes,
                    use_container_width=True,
                    hide_index=True
                )

            st.subheader(
                "💇 Ranking de Serviços"
            )

            if servicos_ranking.empty:

                st.info(
                    "Ainda não existem serviços agendados."
                )

            else:

                st.dataframe(
                    servicos_ranking,
                    use_container_width=True,
                    hide_index=True
                )

        # ==================================================
        # ARQUIVOS PARA DOWNLOAD
        # ==================================================
        resumo_df = pd.DataFrame(
            {
                "Indicador": [
                    "Período inicial",
                    "Período final",
                    "Clientes cadastradas",
                    "Atendimentos",
                    "Total em vendas",
                    "Itens vendidos",
                    "Ticket médio",
                    "Entradas",
                    "Saídas",
                    "Saldo",
                    "Serviço campeão",
                    "Cliente VIP",
                    "Produto campeão",
                    "Pagamento principal"
                ],
                "Resultado": [
                    data_inicial.strftime(
                        "%d/%m/%Y"
                    ),
                    data_final.strftime(
                        "%d/%m/%Y"
                    ),
                    int(clientes_total),
                    total_atendimentos,
                    total_vendas,
                    itens_vendidos,
                    ticket_medio,
                    total_entradas,
                    total_saidas,
                    saldo,
                    servico_campeao,
                    cliente_vip,
                    produto_campeao,
                    pagamento_campeao
                ]
            }
        )

        rankings_df = pd.DataFrame(
            {
                "Categoria": [
                    "Serviço campeão",
                    "Cliente VIP",
                    "Produto campeão",
                    "Pagamento principal"
                ],
                "Resultado": [
                    servico_campeao,
                    cliente_vip,
                    produto_campeao,
                    pagamento_campeao
                ]
            }
        )

        arquivo_excel = criar_excel(
            vendas_df,
            financeiro_df,
            agendamentos_df,
            resumo_df,
            rankings_df
        )

        arquivo_pdf = criar_pdf(
            data_inicial=data_inicial,
            data_final=data_final,
            clientes_total=clientes_total,
            total_atendimentos=total_atendimentos,
            total_vendas=total_vendas,
            itens_vendidos=itens_vendidos,
            ticket_medio=ticket_medio,
            total_entradas=total_entradas,
            total_saidas=total_saidas,
            saldo=saldo,
            servico_campeao=servico_campeao,
            cliente_vip=cliente_vip,
            produto_campeao=produto_campeao,
            pagamento_campeao=pagamento_campeao,
            vendas_df=vendas_df,
            financeiro_df=financeiro_df,
            agendamentos_df=agendamentos_df
        )

        st.markdown("---")

        st.subheader(
            "📥 Exportar Relatório"
        )

        coluna_excel, coluna_pdf = st.columns(
            2
        )

        with coluna_excel:

            st.download_button(
                label="📊 Baixar Relatório em Excel",
                data=arquivo_excel,
                file_name=(
                    f"relatorio_beautyflow_"
                    f"{data_inicial}_"
                    f"{data_final}.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),
                use_container_width=True
            )

        with coluna_pdf:

            st.download_button(
                label="📄 Baixar Relatório em PDF",
                data=arquivo_pdf,
                file_name=(
                    f"relatorio_beautyflow_"
                    f"{data_inicial}_"
                    f"{data_final}.pdf"
                ),
                mime="application/pdf",
                use_container_width=True
            )

        st.caption(
            "BeautyFlow CRM • "
            "Desenvolvido por Luciana Oliveira de Albuquerque"
        )

    finally:

        conn.close()
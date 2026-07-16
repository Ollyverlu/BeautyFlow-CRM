
from datetime import date, datetime
import random

import pandas as pd
import streamlit as st

from banco import conectar
from config import LIMITE_ESTOQUE_BAIXO
from pagina.dashboard_cards import mostrar_cards_premium
from pagina.dashboard_meta import mostrar_meta_diaria
from pagina.dashboard_comissoes import (
    mostrar_painel_atendimentos_dashboard               

)

# ==================================================
# TEXTOS DO DASHBOARD
# ==================================================
FRASES_MOTIVACIONAIS = [
    "Seu talento transforma pessoas. O BeautyFlow cuida da gestão.",
    "Cada cliente satisfeita fortalece o seu negócio.",
    "Organização é o primeiro passo para crescer.",
    "Seu talento encanta. Nossa tecnologia organiza.",
    "Um atendimento especial começa com uma agenda organizada.",
    "Cuidar do seu negócio também é uma forma de cuidar das suas clientes."
]


DICAS_DO_DIA = [
    "Confirme os atendimentos de amanhã pelo WhatsApp.",
    "Confira os produtos com estoque baixo antes de iniciar o dia.",
    "Mantenha as observações das clientes sempre atualizadas.",
    "Registre todas as entradas e saídas para controlar o lucro corretamente.",
    "Clientes que retornam regularmente fortalecem o seu negócio.",
    "Uma agenda organizada reduz atrasos e melhora o atendimento.",
    "Acompanhe o ticket médio para entender o desempenho das vendas.",
    "Faça contato com clientes que estão há muito tempo sem retornar."
]


DIAS_SEMANA = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo"
]


MESES = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro"
]


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================
def saudacao_por_horario():

    hora = datetime.now().hour

    if hora < 12:
        return "🌅 Bom dia"

    if hora < 18:
        return "☀️ Boa tarde"

    return "🌙 Boa noite"


def data_em_portugues():

    agora = datetime.now()

    nome_dia = DIAS_SEMANA[
        agora.weekday()
    ]

    nome_mes = MESES[
        agora.month - 1
    ]

    return (
        f"{nome_dia}, "
        f"{agora.day} de {nome_mes} de {agora.year}"
    )


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


# ==================================================
# DASHBOARD
# ==================================================
def mostrar_dashboard():

    agora = datetime.now()

    hoje = str(
        date.today()
    )

    horario_atual = agora.strftime(
        "%H:%M:%S"
    )

    mes_dia_atual = agora.strftime(
        "%m-%d"
    )

    usuario = st.session_state.get(
        "usuario",
        "Usuário"
    )

    saudacao = saudacao_por_horario()

    data_formatada = data_em_portugues()

    # Mantém a mesma frase durante a sessão
    if "frase_dashboard" not in st.session_state:

        st.session_state["frase_dashboard"] = random.choice(
            FRASES_MOTIVACIONAIS
        )

    # Mantém a mesma dica durante a sessão
    if "dica_dashboard" not in st.session_state:

        st.session_state["dica_dashboard"] = random.choice(
            DICAS_DO_DIA
        )

    frase = st.session_state[
        "frase_dashboard"
    ]

    dica = st.session_state[
        "dica_dashboard"
    ]

    # ==================================================
    # CABEÇALHO
    # ==================================================
    st.title(
        "✨ BeautyFlow CRM"
    )

    st.caption(
        "Onde a beleza encontra a organização"
    )

    st.subheader(
        f"{saudacao}, {usuario}! 🌸"
    )

    st.write(
        f"📅 **{data_formatada.capitalize()}**"
    )

    st.info(
        f"💖 {frase}"
    )

    st.markdown("---")

    # ==================================================
    # CONEXÃO COM O BANCO
    # ==================================================
    conn = conectar()

    try:

        # ==================================================
        # DADOS GERAIS
        # ==================================================
        total_clientes = pd.read_sql_query(
            """
            SELECT COUNT(*) AS total
            FROM clientes
            """,
            conn
        )["total"][0]

        total_agendamentos = pd.read_sql_query(
            """
            SELECT COUNT(*) AS total
            FROM agendamentos
            """,
            conn
        )["total"][0]

        agendamentos_hoje = pd.read_sql_query(
            """
            SELECT COUNT(*) AS total
            FROM agendamentos
            WHERE data = ?
            """,
            conn,
            params=(hoje,)
        )["total"][0]

        total_produtos = pd.read_sql_query(
            """
            SELECT COUNT(*) AS total
            FROM produtos
            """,
            conn
        )["total"][0]

        estoque_baixo_total = pd.read_sql_query(
            """
            SELECT COUNT(*) AS total
            FROM produtos
            WHERE quantidade <= ?
            """,
            conn,
            params=(
                LIMITE_ESTOQUE_BAIXO,
            )
        )["total"][0]

        faturamento_total = pd.read_sql_query(
            """
            SELECT IFNULL(
                SUM(valor_total),
                0
            ) AS total
            FROM vendas
            """,
            conn
        )["total"][0]

        faturamento_hoje = pd.read_sql_query(
            """
            SELECT IFNULL(
                SUM(valor_total),
                0
            ) AS total
            FROM vendas
            WHERE data = ?
            """,
            conn,
            params=(hoje,)
        )["total"][0]

        quantidade_vendas = pd.read_sql_query(
            """
            SELECT COUNT(*) AS total
            FROM vendas
            """,
            conn
        )["total"][0]

        total_entradas = pd.read_sql_query(
            """
            SELECT IFNULL(
                SUM(valor),
                0
            ) AS total
            FROM financeiro
            WHERE tipo = 'Entrada'
            """,
            conn
        )["total"][0]

        total_saidas = pd.read_sql_query(
            """
            SELECT IFNULL(
                SUM(valor),
                0
            ) AS total
            FROM financeiro
            WHERE tipo = 'Saída'
            """,
            conn
        )["total"][0]

        saldo_financeiro = (
            float(total_entradas)
            - float(total_saidas)
        )

        if quantidade_vendas > 0:

            ticket_medio = (
                float(faturamento_total)
                / int(quantidade_vendas)
            )

        else:

            ticket_medio = 0.0

        # ==================================================
        # PRÓXIMO ATENDIMENTO
        # ==================================================
        proximo_atendimento = pd.read_sql_query(
            """
            SELECT
                cliente,
                data,
                horario,
                servico
            FROM agendamentos
            WHERE
                data > ?
                OR (
                    data = ?
                    AND horario >= ?
                )
            ORDER BY
                data ASC,
                horario ASC
            LIMIT 1
            """,
            conn,
            params=(
                hoje,
                hoje,
                horario_atual
            )
        )

        # ==================================================
        # ANIVERSARIANTES
        # ==================================================
        aniversariantes = pd.read_sql_query(
            """
            SELECT
                nome,
                telefone
            FROM clientes
            WHERE
                nascimento IS NOT NULL
                AND nascimento != ''
                AND SUBSTR(
                    nascimento,
                    6,
                    5
                ) = ?
            ORDER BY nome
            """,
            conn,
            params=(
                mes_dia_atual,
            )
        )
        
        mostrar_cards_premium()

        st.markdown("---")
        
        mostrar_meta_diaria()

        st.markdown("---")

        # ==================================================
        # RESUMO DO DIA
        # ==================================================
        st.subheader(
            "🌸 Resumo do Dia"
        )

        resumo1, resumo2, resumo3, resumo4 = st.columns(
            4
        )

        with resumo1:

            st.metric(
                label="📅 Agendamentos hoje",
                value=int(
                    agendamentos_hoje
                )
            )

        with resumo2:

            st.metric(
                label="💵 Vendas de hoje",
                value=formatar_moeda(
                    faturamento_hoje
                )
            )

        with resumo3:

            st.metric(
                label="⚠️ Produtos para repor",
                value=int(
                    estoque_baixo_total
                )
            )

        with resumo4:

            st.metric(
                label="📈 Saldo financeiro",
                value=formatar_moeda(
                    saldo_financeiro
                )
            )

        st.markdown("---")

        # ==================================================
        # PAINEL INTELIGENTE
        # ==================================================
        st.subheader(
            "✨ Painel Inteligente"
        )

        coluna_proximo, coluna_aniversario, coluna_dica = st.columns(
            3
        )

        with coluna_proximo:

            st.subheader(
                "⭐ Próximo Atendimento"
            )

            if proximo_atendimento.empty:

                st.info(
                    "Nenhum atendimento futuro encontrado."
                )

            else:

                proximo = proximo_atendimento.iloc[0]

                st.metric(
                    label="⏰ Horário",
                    value=formatar_horario(
                        proximo["horario"]
                    )
                )

                st.write(
                    f"👩 **Cliente:** "
                    f"{proximo['cliente']}"
                )

                st.write(
                    f"💇 **Serviço:** "
                    f"{proximo['servico']}"
                )

                st.write(
                    f"📅 **Data:** "
                    f"{formatar_data_br(proximo['data'])}"
                )

        with coluna_aniversario:

            st.subheader(
                "🎂 Aniversariantes"
            )

            if aniversariantes.empty:

                st.info(
                    "Nenhuma aniversariante hoje."
                )

            else:

                st.success(
                    f"Hoje temos "
                    f"{len(aniversariantes)} "
                    f"aniversariante(s)! 🎉"
                )

                for _, cliente in aniversariantes.iterrows():

                    st.write(
                        f"🎁 **{cliente['nome']}**"
                    )

                    telefone = cliente[
                        "telefone"
                    ]

                    if (
                        telefone is not None
                        and str(
                            telefone
                        ).strip() != ""
                    ):

                        st.caption(
                            f"📱 {telefone}"
                        )

        with coluna_dica:

            st.subheader(
                "💡 Dica do Dia"
            )

            st.info(
                dica
            )

            if st.button(
                "🔄 Nova dica",
                key="nova_dica_dashboard",
                use_container_width=True
            ):

                novas_dicas = [
                    item
                    for item in DICAS_DO_DIA
                    if item != dica
                ]

                st.session_state[
                    "dica_dashboard"
                ] = random.choice(
                    novas_dicas
                )

                st.rerun()

        st.markdown("---") 

        mostrar_painel_atendimentos_dashboard()

        st.markdown("---")
        
        # ==================================================
        # VISÃO GERAL
        # ==================================================
        st.subheader(
            "📌 Visão Geral"
        )

        coluna1, coluna2, coluna3, coluna4 = st.columns(
            4
        )

        with coluna1:

            st.metric(
                label="👩‍💼 Clientes",
                value=int(
                    total_clientes
                )
            )

        with coluna2:

            st.metric(
                label="📅 Agendamentos",
                value=int(
                    total_agendamentos
                ),
                delta=(
                    f"{int(agendamentos_hoje)} hoje"
                )
            )

        with coluna3:

            st.metric(
                label="🛍️ Produtos",
                value=int(
                    total_produtos
                )
            )

        with coluna4:

            st.metric(
                label="⚠️ Estoque baixo",
                value=int(
                    estoque_baixo_total
                )
            )

        coluna5, coluna6, coluna7, coluna8 = st.columns(
            4
        )

        with coluna5:

            st.metric(
                label="💰 Faturamento total",
                value=formatar_moeda(
                    faturamento_total
                )
            )

        with coluna6:

            st.metric(
                label="💵 Vendas de hoje",
                value=formatar_moeda(
                    faturamento_hoje
                )
            )

        with coluna7:

            st.metric(
                label="🎯 Ticket médio",
                value=formatar_moeda(
                    ticket_medio
                )
            )

        with coluna8:

            st.metric(
                label="📈 Saldo financeiro",
                value=formatar_moeda(
                    saldo_financeiro
                )
            )

        st.markdown("---")

        # ==================================================
        # AGENDA E ESTOQUE
        # ==================================================
        coluna_agenda, coluna_estoque = st.columns(
            2
        )

        with coluna_agenda:

            st.subheader(
                "📅 Próximos Agendamentos"
            )

            proximos_agendamentos = pd.read_sql_query(
                """
                SELECT
                    cliente AS Cliente,
                    data AS Data,
                    horario AS Horário,
                    servico AS Serviço
                FROM agendamentos
                WHERE data >= ?
                ORDER BY
                    data ASC,
                    horario ASC
                LIMIT 5
                """,
                conn,
                params=(hoje,)
            )

            if proximos_agendamentos.empty:

                st.info(
                    "Nenhum agendamento futuro encontrado."
                )

            else:

                proximos_agendamentos[
                    "Data"
                ] = proximos_agendamentos[
                    "Data"
                ].apply(
                    formatar_data_br
                )

                proximos_agendamentos[
                    "Horário"
                ] = proximos_agendamentos[
                    "Horário"
                ].apply(
                    formatar_horario
                )

                st.dataframe(
                    proximos_agendamentos,
                    use_container_width=True,
                    hide_index=True
                )

        with coluna_estoque:

            st.subheader(
                "📦 Produtos para Reposição"
            )

            estoque_baixo = pd.read_sql_query(
                """
                SELECT
                    nome AS Produto,
                    categoria AS Categoria,
                    quantidade AS Estoque
                FROM produtos
                WHERE quantidade <= ?
                ORDER BY
                    quantidade ASC,
                    nome ASC
                """,
                conn,
                params=(
                    LIMITE_ESTOQUE_BAIXO,
                )
            )

            if estoque_baixo.empty:

                st.success(
                    "✅ Todos os produtos estão "
                    "com estoque adequado."
                )

            else:

                st.warning(
                    "Alguns produtos precisam de reposição."
                )

                st.dataframe(
                    estoque_baixo,
                    use_container_width=True,
                    hide_index=True
                )

        st.markdown("---")

        # ==================================================
        # GRÁFICOS
        # ==================================================
        coluna_grafico1, coluna_grafico2 = st.columns(
            2
        )

        with coluna_grafico1:

            st.subheader(
                "📊 Faturamento por Data"
            )

            vendas_por_data = pd.read_sql_query(
                """
                SELECT
                    data,
                    SUM(valor_total) AS faturamento
                FROM vendas
                GROUP BY data
                ORDER BY data ASC
                """,
                conn
            )

            if vendas_por_data.empty:

                st.info(
                    "Ainda não existem vendas "
                    "para gerar o gráfico."
                )

            else:

                vendas_por_data = (
                    vendas_por_data
                    .set_index("data")
                )

                st.bar_chart(
                    vendas_por_data[
                        "faturamento"
                    ]
                )

        with coluna_grafico2:

            st.subheader(
                "🏆 Produtos Mais Vendidos"
            )

            produtos_mais_vendidos = pd.read_sql_query(
                """
                SELECT
                    produto,
                    SUM(quantidade) AS quantidade
                FROM vendas
                GROUP BY produto
                ORDER BY quantidade DESC
                LIMIT 5
                """,
                conn
            )

            if produtos_mais_vendidos.empty:

                st.info(
                    "Ainda não existem produtos vendidos."
                )

            else:

                produtos_mais_vendidos = (
                    produtos_mais_vendidos
                    .set_index("produto")
                )

                st.bar_chart(
                    produtos_mais_vendidos[
                        "quantidade"
                    ]
                )

        st.markdown("---")

        # ==================================================
        # RESUMO FINANCEIRO
        # ==================================================
        st.subheader(
            "💳 Resumo Financeiro"
        )

        financeiro_resumo = pd.DataFrame(
            {
                "Categoria": [
                    "Entradas",
                    "Saídas",
                    "Saldo"
                ],
                "Valor": [
                    float(
                        total_entradas
                    ),
                    float(
                        total_saidas
                    ),
                    float(
                        saldo_financeiro
                    )
                ]
            }
        )

        financeiro_resumo = financeiro_resumo.set_index(
            "Categoria"
        )

        st.bar_chart(
            financeiro_resumo[
                "Valor"
            ]
        )

        st.markdown("---")

        st.caption(
            "BeautyFlow CRM • "
            "Desenvolvido por Luciana Ollyver"
        )

    finally:

        conn.close()

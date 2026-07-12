
from datetime import date, datetime, time
from urllib.parse import quote
import re

import pandas as pd
import streamlit as st

from banco import conectar


WHATSAPP_ESTABELECIMENTO = "5521988219493"

LISTA_SERVICOS = [
    "Extensão de Cílios",
    "Manutenção de Cílios",
    "Balayagem",
    "Strong",
    "Morena Iluminada",
    "Retoque de Mechas",
    "Corte de Cabelo",
    "Escova Curta",
    "Escova Média",
    "Escova Longa",
    "Hidratação",
    "Reconstrução",
    "Nutrição",
    "Progressiva sem Formol",
    "Botox",
    "Micropigmentação Esfumada",
    "Micropigmentação Fio a Fio"
]


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================
def carregar_agendamentos():

    conn = conectar()

    agenda_df = pd.read_sql_query(
        """
        SELECT *
        FROM agendamentos
        ORDER BY data ASC, horario ASC
        """,
        conn
    )

    conn.close()

    return agenda_df


def carregar_clientes():

    conn = conectar()

    clientes_df = pd.read_sql_query(
        """
        SELECT id, nome, telefone
        FROM clientes
        ORDER BY nome
        """,
        conn
    )

    conn.close()

    return clientes_df


def converter_data(valor):

    try:
        return datetime.strptime(
            str(valor),
            "%Y-%m-%d"
        ).date()

    except (ValueError, TypeError):
        return date.today()


def converter_horario(valor):

    texto = str(valor)

    formatos = [
        "%H:%M:%S",
        "%H:%M"
    ]

    for formato in formatos:

        try:
            return datetime.strptime(
                texto,
                formato
            ).time()

        except ValueError:
            continue

    return time(9, 0)


def formatar_data_br(valor):

    try:
        data_convertida = datetime.strptime(
            str(valor),
            "%Y-%m-%d"
        )

        return data_convertida.strftime(
            "%d/%m/%Y"
        )

    except ValueError:
        return str(valor)


def formatar_horario(valor):

    try:
        horario_convertido = datetime.strptime(
            str(valor),
            "%H:%M:%S"
        )

        return horario_convertido.strftime(
            "%H:%M"
        )

    except ValueError:

        try:
            horario_convertido = datetime.strptime(
                str(valor),
                "%H:%M"
            )

            return horario_convertido.strftime(
                "%H:%M"
            )

        except ValueError:
            return str(valor)


def buscar_telefone_cliente(nome_cliente):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT telefone
        FROM clientes
        WHERE LOWER(nome) = LOWER(?)
        LIMIT 1
        """,
        (nome_cliente,)
    )

    resultado = cursor.fetchone()

    conn.close()

    if resultado and resultado[0]:
        return str(resultado[0])

    return ""


def criar_link_whatsapp(
    cliente,
    servico,
    data_atendimento,
    horario_atendimento,
    telefone_cliente=""
):

    data_formatada = formatar_data_br(
        data_atendimento
    )

    horario_formatado = formatar_horario(
        horario_atendimento
    )

    mensagem = (
        f"Olá, {cliente}! 🌸\n\n"
        f"Seu agendamento no BeautyFlow CRM "
        f"está confirmado.\n\n"
        f"💇 Serviço: {servico}\n"
        f"📅 Data: {data_formatada}\n"
        f"⏰ Horário: {horario_formatado}\n\n"
        f"Aguardamos você! ✨"
    )

    telefone_numeros = re.sub(
        r"\D",
        "",
        telefone_cliente
    )

    if telefone_numeros:

        if not telefone_numeros.startswith("55"):
            telefone_numeros = (
                "55"
                + telefone_numeros
            )

        return (
            f"https://wa.me/{telefone_numeros}"
            f"?text={quote(mensagem)}"
        )

    return (
        f"https://wa.me/{WHATSAPP_ESTABELECIMENTO}"
        f"?text={quote(mensagem)}"
    )


def verificar_horario_ocupado(
    data_atendimento,
    horario_atendimento,
    ignorar_id=None
):

    conn = conectar()
    cursor = conn.cursor()

    if ignorar_id is None:

        cursor.execute(
            """
            SELECT id
            FROM agendamentos
            WHERE data = ?
            AND horario = ?
            """,
            (
                str(data_atendimento),
                str(horario_atendimento)
            )
        )

    else:

        cursor.execute(
            """
            SELECT id
            FROM agendamentos
            WHERE data = ?
            AND horario = ?
            AND id != ?
            """,
            (
                str(data_atendimento),
                str(horario_atendimento),
                ignorar_id
            )
        )

    resultado = cursor.fetchone()

    conn.close()

    return resultado is not None


def preparar_tabela_agenda(agenda_df):

    if agenda_df.empty:
        return agenda_df

    tabela = agenda_df.copy()

    tabela["Data"] = tabela["data"].apply(
        formatar_data_br
    )

    tabela["Horário"] = tabela["horario"].apply(
        formatar_horario
    )

    tabela["Cliente"] = tabela["cliente"]

    tabela["Serviço"] = tabela["servico"]

    tabela["Status"] = "🩷 Agendado"

    return tabela[
        [
            "Data",
            "Horário",
            "Cliente",
            "Serviço",
            "Status"
        ]
    ]


# ==================================================
# PÁGINA PRINCIPAL
# ==================================================
def mostrar_agenda():

    st.title("📅 Agenda BeautyFlow")

    st.caption(
        "Organize os horários, consulte o dia "
        "e confirme atendimentos pelo WhatsApp."
    )

    aba1, aba2, aba3, aba4 = st.tabs(
        [
            "➕ Novo Agendamento",
            "📆 Agenda do Dia",
            "✏️ Editar",
            "🗑️ Cancelar"
        ]
    )

    # ==================================================
    # NOVO AGENDAMENTO
    # ==================================================
    with aba1:

        st.subheader(
            "➕ Novo Agendamento"
        )

        clientes_df = carregar_clientes()

        usar_cliente_cadastrada = st.checkbox(
            "Selecionar uma cliente cadastrada",
            value=not clientes_df.empty,
            key="usar_cliente_cadastrada"
        )

        if usar_cliente_cadastrada and not clientes_df.empty:

            clientes_df["opcao"] = (
                clientes_df["id"].astype(str)
                + " - "
                + clientes_df["nome"]
            )

            cliente_opcao = st.selectbox(
                "Cliente",
                clientes_df["opcao"].tolist(),
                key="agenda_cliente_lista"
            )

            cliente_id = int(
                cliente_opcao.split(" - ")[0]
            )

            cliente_linha = clientes_df[
                clientes_df["id"] == cliente_id
            ].iloc[0]

            cliente = str(
                cliente_linha["nome"]
            )

            telefone_cliente = str(
                cliente_linha["telefone"]
                if cliente_linha["telefone"] is not None
                else ""
            )

            st.info(
                f"📱 WhatsApp: "
                f"{telefone_cliente or 'Não informado'}"
            )

        else:

            cliente = st.text_input(
                "Nome da cliente",
                key="agenda_cliente_manual"
            )

            telefone_cliente = st.text_input(
                "WhatsApp da cliente",
                placeholder="Exemplo: 21999999999",
                key="agenda_telefone_manual"
            )

        coluna_data, coluna_horario = st.columns(2)

        with coluna_data:

            data_atendimento = st.date_input(
                "Data do atendimento",
                value=date.today(),
                format="DD/MM/YYYY",
                key="agenda_data"
            )

        with coluna_horario:

            horario_atendimento = st.time_input(
                "Horário",
                value=time(9, 0),
                step=1800,
                key="agenda_horario"
            )

        servico = st.selectbox(
            "Serviço",
            LISTA_SERVICOS,
            key="agenda_servico"
        )

        st.info(
            f"📌 Agendamento: {cliente or 'Cliente'} • "
            f"{servico} • "
            f"{data_atendimento.strftime('%d/%m/%Y')} • "
            f"{horario_atendimento.strftime('%H:%M')}"
        )

        if st.button(
            "📅 Confirmar Agendamento",
            key="btn_agendar",
            use_container_width=True
        ):

            if cliente.strip() == "":

                st.error(
                    "Digite ou selecione o nome da cliente."
                )

            elif verificar_horario_ocupado(
                data_atendimento,
                horario_atendimento
            ):

                st.error(
                    "Este horário já possui um agendamento. "
                    "Escolha outro horário."
                )

            else:

                conn = conectar()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO agendamentos
                    (
                        cliente,
                        data,
                        horario,
                        servico
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        cliente.strip(),
                        str(data_atendimento),
                        str(horario_atendimento),
                        servico
                    )
                )

                conn.commit()
                conn.close()

                st.success(
                    "Agendamento salvo com sucesso!"
                )

                link = criar_link_whatsapp(
                    cliente=cliente.strip(),
                    servico=servico,
                    data_atendimento=data_atendimento,
                    horario_atendimento=horario_atendimento,
                    telefone_cliente=telefone_cliente
                )

                st.link_button(
                    "💬 Enviar confirmação pelo WhatsApp",
                    link,
                    use_container_width=True
                )

    # ==================================================
    # AGENDA DO DIA
    # ==================================================
    with aba2:

        st.subheader(
            "📆 Agenda do Dia"
        )

        data_consulta = st.date_input(
            "Escolha a data",
            value=date.today(),
            format="DD/MM/YYYY",
            key="consulta_data_agenda"
        )

        agenda_df = carregar_agendamentos()

        agenda_dia = agenda_df[
            agenda_df["data"].astype(str)
            == str(data_consulta)
        ].copy()

        quantidade_atendimentos = len(
            agenda_dia
        )

        coluna1, coluna2 = st.columns(2)

        with coluna1:

            st.metric(
                "📅 Atendimentos do dia",
                quantidade_atendimentos
            )

        with coluna2:

            if quantidade_atendimentos > 0:

                primeiro_horario = (
                    agenda_dia
                    .sort_values("horario")
                    .iloc[0]["horario"]
                )

                st.metric(
                    "⏰ Primeiro horário",
                    formatar_horario(
                        primeiro_horario
                    )
                )

            else:

                st.metric(
                    "⏰ Primeiro horário",
                    "--"
                )

        st.markdown("---")

        if agenda_dia.empty:

            st.success(
                "🟢 Nenhum atendimento agendado "
                "para esta data."
            )

        else:

            agenda_dia = agenda_dia.sort_values(
                "horario"
            )

            tabela_dia = preparar_tabela_agenda(
                agenda_dia
            )

            st.dataframe(
                tabela_dia,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")

            st.subheader(
                "🩷 Detalhes dos Atendimentos"
            )

            for _, atendimento in agenda_dia.iterrows():

                horario = formatar_horario(
                    atendimento["horario"]
                )

                titulo = (
                    f"🩷 {horario} — "
                    f"{atendimento['cliente']} — "
                    f"{atendimento['servico']}"
                )

                with st.expander(
                    titulo
                ):

                    st.write(
                        f"👩 **Cliente:** "
                        f"{atendimento['cliente']}"
                    )

                    st.write(
                        f"💇 **Serviço:** "
                        f"{atendimento['servico']}"
                    )

                    st.write(
                        f"📅 **Data:** "
                        f"{formatar_data_br(atendimento['data'])}"
                    )

                    st.write(
                        f"⏰ **Horário:** "
                        f"{horario}"
                    )

                    telefone = buscar_telefone_cliente(
                        atendimento["cliente"]
                    )

                    link = criar_link_whatsapp(
                        cliente=atendimento["cliente"],
                        servico=atendimento["servico"],
                        data_atendimento=atendimento["data"],
                        horario_atendimento=atendimento["horario"],
                        telefone_cliente=telefone
                    )

                    st.link_button(
                        "💬 Confirmar pelo WhatsApp",
                        link,
                        use_container_width=True
                    )

    # ==================================================
    # EDITAR AGENDAMENTO
    # ==================================================
    with aba3:

        st.subheader(
            "✏️ Editar Agendamento"
        )

        agenda_df = carregar_agendamentos()

        if agenda_df.empty:

            st.info(
                "Ainda não existem agendamentos."
            )

        else:

            agenda_df["opcao"] = (
                agenda_df["id"].astype(str)
                + " - "
                + agenda_df["cliente"]
                + " - "
                + agenda_df["data"].apply(
                    formatar_data_br
                )
                + " - "
                + agenda_df["horario"].apply(
                    formatar_horario
                )
                + " - "
                + agenda_df["servico"]
            )

            escolhido = st.selectbox(
                "Escolha o agendamento",
                agenda_df["opcao"].tolist(),
                key="editar_agendamento"
            )

            agendamento_id = int(
                escolhido.split(" - ")[0]
            )

            linha = agenda_df[
                agenda_df["id"]
                == agendamento_id
            ].iloc[0]

            novo_cliente = st.text_input(
                "Nome da cliente",
                value=str(
                    linha["cliente"]
                ),
                key="edit_agenda_cliente"
            )

            coluna_data, coluna_horario = st.columns(2)

            with coluna_data:

                nova_data = st.date_input(
                    "Data do atendimento",
                    value=converter_data(
                        linha["data"]
                    ),
                    format="DD/MM/YYYY",
                    key="edit_agenda_data"
                )

            with coluna_horario:

                novo_horario = st.time_input(
                    "Horário",
                    value=converter_horario(
                        linha["horario"]
                    ),
                    step=1800,
                    key="edit_agenda_horario"
                )

            servico_atual = str(
                linha["servico"]
            )

            if servico_atual in LISTA_SERVICOS:

                indice = LISTA_SERVICOS.index(
                    servico_atual
                )

            else:

                indice = 0

            novo_servico = st.selectbox(
                "Serviço",
                LISTA_SERVICOS,
                index=indice,
                key="edit_agenda_servico"
            )

            if st.button(
                "💾 Salvar Alterações",
                key="btn_editar_agenda",
                use_container_width=True
            ):

                if novo_cliente.strip() == "":

                    st.error(
                        "O nome da cliente "
                        "não pode ficar vazio."
                    )

                elif verificar_horario_ocupado(
                    nova_data,
                    novo_horario,
                    ignorar_id=agendamento_id
                ):

                    st.error(
                        "Já existe outro agendamento "
                        "neste horário."
                    )

                else:

                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        UPDATE agendamentos
                        SET
                            cliente = ?,
                            data = ?,
                            horario = ?,
                            servico = ?
                        WHERE id = ?
                        """,
                        (
                            novo_cliente.strip(),
                            str(nova_data),
                            str(novo_horario),
                            novo_servico,
                            agendamento_id
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "Agendamento atualizado "
                        "com sucesso!"
                    )

                    telefone = buscar_telefone_cliente(
                        novo_cliente
                    )

                    link = criar_link_whatsapp(
                        cliente=novo_cliente,
                        servico=novo_servico,
                        data_atendimento=nova_data,
                        horario_atendimento=novo_horario,
                        telefone_cliente=telefone
                    )

                    st.link_button(
                        "💬 Enviar nova confirmação",
                        link,
                        use_container_width=True
                    )

    # ==================================================
    # CANCELAR AGENDAMENTO
    # ==================================================
    with aba4:

        st.subheader(
            "🗑️ Cancelar Agendamento"
        )

        agenda_df = carregar_agendamentos()

        if agenda_df.empty:

            st.info(
                "Ainda não existem agendamentos."
            )

        else:

            agenda_df["opcao"] = (
                agenda_df["id"].astype(str)
                + " - "
                + agenda_df["cliente"]
                + " - "
                + agenda_df["data"].apply(
                    formatar_data_br
                )
                + " - "
                + agenda_df["horario"].apply(
                    formatar_horario
                )
                + " - "
                + agenda_df["servico"]
            )

            escolhido_excluir = st.selectbox(
                "Escolha o agendamento para cancelar",
                agenda_df["opcao"].tolist(),
                key="excluir_agendamento"
            )

            excluir_id = int(
                escolhido_excluir.split(" - ")[0]
            )

            linha_excluir = agenda_df[
                agenda_df["id"]
                == excluir_id
            ].iloc[0]

            st.warning(
                f"Você está prestes a cancelar o "
                f"agendamento de "
                f"{linha_excluir['cliente']} em "
                f"{formatar_data_br(linha_excluir['data'])} "
                f"às "
                f"{formatar_horario(linha_excluir['horario'])}."
            )

            confirmar = st.checkbox(
                "Confirmo que desejo cancelar "
                "este agendamento",
                key="confirmar_cancelar_agenda"
            )

            if st.button(
                "🗑️ Cancelar Agendamento",
                key="btn_cancelar_agenda",
                use_container_width=True
            ):

                if not confirmar:

                    st.error(
                        "Marque a confirmação "
                        "antes de cancelar."
                    )

                else:

                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        DELETE FROM agendamentos
                        WHERE id = ?
                        """,
                        (excluir_id,)
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "Agendamento cancelado "
                        "com sucesso!"
                    )

                    st.rerun()

    # ==================================================
    # LISTA GERAL
    # ==================================================
    st.markdown("---")

    st.subheader(
        "📋 Todos os Agendamentos"
    )

    lista_agenda = carregar_agendamentos()

    if lista_agenda.empty:

        st.info(
            "Ainda não existem "
            "agendamentos salvos."
        )

    else:

        tabela_geral = preparar_tabela_agenda(
            lista_agenda
        )

        st.dataframe(
            tabela_geral,
            use_container_width=True,
            hide_index=True
        )

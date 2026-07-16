
from datetime import date, datetime
from pathlib import Path
import re
import unicodedata

import pandas as pd
import streamlit as st

from banco import conectar


# ==================================================
# CAMINHOS
# ==================================================
PASTA_PROJETO = Path(__file__).resolve().parent.parent

PASTA_FOTOS_CLIENTES = (
    PASTA_PROJETO
    / "assets"
    / "imagens"
    / "clientes"
)

PASTA_FOTOS_CLIENTES.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# LISTAS
# ==================================================
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
def carregar_clientes():

    conn = conectar()

    clientes_df = pd.read_sql_query(
        """
        SELECT *
        FROM clientes
        ORDER BY nome
        """,
        conn
    )

    conn.close()

    return clientes_df


def texto_seguro(valor):

    if valor is None:
        return ""

    if pd.isna(valor):
        return ""

    return str(valor)


def data_segura(valor):

    if valor is None:
        return date.today()

    if pd.isna(valor):
        return date.today()

    try:
        return datetime.strptime(
            str(valor),
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return date.today()


def nome_arquivo_seguro(nome):

    nome_normalizado = unicodedata.normalize(
        "NFKD",
        nome
    )

    nome_sem_acentos = "".join(
        caractere
        for caractere in nome_normalizado
        if not unicodedata.combining(caractere)
    )

    nome_limpo = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        nome_sem_acentos
    )

    return nome_limpo.lower()


def salvar_foto(arquivo, nome_cliente):

    if arquivo is None:
        return ""

    extensao = Path(
        arquivo.name
    ).suffix.lower()

    if extensao not in [
        ".png",
        ".jpg",
        ".jpeg"
    ]:
        st.error(
            "Envie uma imagem PNG, JPG ou JPEG."
        )

        return ""

    nome_limpo = nome_arquivo_seguro(
        nome_cliente
    )

    momento = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    nome_arquivo = (
        f"{nome_limpo}_{momento}{extensao}"
    )

    caminho_foto = (
        PASTA_FOTOS_CLIENTES
        / nome_arquivo
    )

    with open(
        caminho_foto,
        "wb"
    ) as destino:

        destino.write(
            arquivo.getbuffer()
        )

    return str(caminho_foto)


def calcular_total_gasto(nome_cliente):

    conn = conectar()

    resultado = pd.read_sql_query(
        """
        SELECT IFNULL(
            SUM(valor_total),
            0
        ) AS total
        FROM vendas
        WHERE LOWER(cliente) = LOWER(?)
        """,
        conn,
        params=(nome_cliente,)
    )

    conn.close()

    return float(
        resultado["total"][0]
    )


def formatar_moeda(valor):

    texto = f"{float(valor):,.2f}"

    texto = (
        texto
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


def abrir_whatsapp(telefone):

    apenas_numeros = re.sub(
        r"\D",
        "",
        telefone
    )

    if apenas_numeros == "":
        return ""

    if not apenas_numeros.startswith("55"):
        apenas_numeros = (
            "55"
            + apenas_numeros
        )

    return (
        f"https://wa.me/{apenas_numeros}"
    )


# ==================================================
# PÁGINA CLIENTES
# ==================================================
def mostrar_clientes():

    st.title("👩‍💼 Clientes Premium")

    st.caption(
        "Cadastre, consulte, edite e acompanhe "
        "o histórico das suas clientes."
    )

    aba1, aba2, aba3, aba4, aba5 = st.tabs(
        [
            "➕ Cadastrar",
            "🔎 Pesquisar",
            "👩 Ficha da Cliente",
            "✏️ Editar",
            "🗑️ Excluir"
        ]
    )

    # ==================================================
    # CADASTRAR CLIENTE
    # ==================================================
    with aba1:

        st.subheader(
            "➕ Cadastrar Nova Cliente"
        )

        coluna1, coluna2 = st.columns(2)

        with coluna1:

            nome = st.text_input(
                "Nome completo",
                key="cad_nome"
            )

            telefone = st.text_input(
                "WhatsApp",
                placeholder="Exemplo: 21999999999",
                key="cad_telefone"
            )

            email = st.text_input(
                "E-mail",
                key="cad_email"
            )

            instagram = st.text_input(
                "Instagram",
                placeholder="@usuario",
                key="cad_instagram"
            )

        with coluna2:

            from datetime import date

         
        nascimento = st.date_input(
            "🎂 Data de nascimento",
            value=date(1990, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
            key="cad_nascimento"
)

        endereco = st.text_input(
                "Endereço",
                key="cad_endereco"
            )

        servico_favorito = st.selectbox(
               "Serviço favorito",
                LISTA_SERVICOS,
                key="cad_servico_favorito"
            )

        foto = st.file_uploader(
                "Foto da cliente",
                type=[
                    "png",
                    "jpg",
                    "jpeg"
                ],
                key="cad_foto"
            )

        observacao = st.text_area(
            "Observações",
            placeholder=(
                "Preferências, cuidados, alergias, "
                "melhor horário de atendimento..."
            ),
            key="cad_observacao"
        )

        if st.button(
            "💾 Salvar Cliente",
            use_container_width=True,
            key="btn_salvar_cliente"
        ):

            if nome.strip() == "":

                st.error(
                    "Digite o nome da cliente."
                )

            else:

                caminho_foto = salvar_foto(
                    foto,
                    nome
                )

                conn = conectar()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO clientes
                    (
                        nome,
                        telefone,
                        servico,
                        observacao,
                        email,
                        instagram,
                        nascimento,
                        endereco,
                        servico_favorito,
                        total_gasto,
                        foto
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        nome.strip(),
                        telefone.strip(),
                        servico_favorito,
                        observacao.strip(),
                        email.strip(),
                        instagram.strip(),
                        str(nascimento),
                        endereco.strip(),
                        servico_favorito,
                        0.0,
                        caminho_foto
                    )
                )

                conn.commit()
                conn.close()

                st.success(
                    f"Cliente {nome} cadastrada "
                    "com sucesso!"
                )

                st.rerun()

    # ==================================================
    # PESQUISAR CLIENTE
    # ==================================================
    with aba2:

        st.subheader(
            "🔎 Pesquisar Cliente"
        )

        busca = st.text_input(
            "Digite nome, telefone, e-mail ou Instagram",
            key="busca_cliente"
        )

        clientes_df = carregar_clientes()

        if clientes_df.empty:

            st.info(
                "Ainda não existem clientes cadastradas."
            )

        else:

            resultado_df = clientes_df.copy()

            if busca.strip() != "":

                busca_normalizada = (
                    busca
                    .strip()
                    .lower()
                )

                colunas_busca = [
                    "nome",
                    "telefone",
                    "email",
                    "instagram"
                ]

                filtro_total = pd.Series(
                    False,
                    index=resultado_df.index
                )

                for coluna in colunas_busca:

                    if coluna in resultado_df.columns:

                        filtro_coluna = (
                            resultado_df[coluna]
                            .fillna("")
                            .astype(str)
                            .str.lower()
                            .str.contains(
                                busca_normalizada,
                                regex=False
                            )
                        )

                        filtro_total = (
                            filtro_total
                            | filtro_coluna
                        )

                resultado_df = resultado_df[
                    filtro_total
                ]

            st.write(
                f"**Clientes encontradas:** "
                f"{len(resultado_df)}"
            )

            if resultado_df.empty:

                st.warning(
                    "Nenhuma cliente encontrada."
                )

            else:

                colunas_exibir = [
                    "id",
                    "nome",
                    "telefone",
                    "email",
                    "instagram",
                    "nascimento",
                    "servico_favorito"
                ]

                colunas_existentes = [
                    coluna
                    for coluna in colunas_exibir
                    if coluna in resultado_df.columns
                ]

                st.dataframe(
                    resultado_df[
                        colunas_existentes
                    ],
                    use_container_width=True,
                    hide_index=True
                )

    # ==================================================
    # FICHA DA CLIENTE
    # ==================================================
    with aba3:

        st.subheader(
            "👩 Ficha Completa da Cliente"
        )

        clientes_df = carregar_clientes()

        if clientes_df.empty:

            st.info(
                "Ainda não existem clientes cadastradas."
            )

        else:

            clientes_df["opcao"] = (
                clientes_df["id"].astype(str)
                + " - "
                + clientes_df["nome"]
            )

            cliente_selecionada = st.selectbox(
                "Escolha a cliente",
                clientes_df["opcao"].tolist(),
                key="ficha_cliente"
            )

            cliente_id = int(
                cliente_selecionada
                .split(" - ")[0]
            )

            cliente = clientes_df[
                clientes_df["id"]
                == cliente_id
            ].iloc[0]

            nome_cliente = texto_seguro(
                cliente["nome"]
            )

            telefone_cliente = texto_seguro(
                cliente["telefone"]
            )

            total_gasto = calcular_total_gasto(
                nome_cliente
            )

            coluna_foto, coluna_dados = st.columns(
                [1, 2]
            )

            with coluna_foto:

                caminho_foto = texto_seguro(
                    cliente.get(
                        "foto",
                        ""
                    )
                )

                if (
                    caminho_foto != ""
                    and Path(
                        caminho_foto
                    ).exists()
                ):

                    st.image(
                        caminho_foto,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "📷 Cliente sem foto cadastrada."
                    )

            with coluna_dados:

                st.title(
                    f"👩 {nome_cliente}"
                )

                st.write(
                    f"📱 **WhatsApp:** "
                    f"{telefone_cliente or 'Não informado'}"
                )

                st.write(
                    f"📧 **E-mail:** "
                    f"{texto_seguro(cliente.get('email')) or 'Não informado'}"
                )

                st.write(
                    f"📸 **Instagram:** "
                    f"{texto_seguro(cliente.get('instagram')) or 'Não informado'}"
                )

                st.write(
                    f"🎂 **Nascimento:** "
                    f"{texto_seguro(cliente.get('nascimento')) or 'Não informado'}"
                )

                st.write(
                    f"📍 **Endereço:** "
                    f"{texto_seguro(cliente.get('endereco')) or 'Não informado'}"
                )

                st.write(
                    f"💇 **Serviço favorito:** "
                    f"{texto_seguro(cliente.get('servico_favorito')) or 'Não informado'}"
                )

                st.metric(
                    "💰 Total gasto",
                    formatar_moeda(
                        total_gasto
                    )
                )

                link_whatsapp = abrir_whatsapp(
                    telefone_cliente
                )

                if link_whatsapp != "":

                    st.link_button(
                        "💬 Abrir WhatsApp",
                        link_whatsapp,
                        use_container_width=True
                    )

            st.markdown("---")

            st.subheader(
                "⭐ Observações"
            )

            observacao_cliente = texto_seguro(
                cliente.get(
                    "observacao",
                    ""
                )
            )

            if observacao_cliente == "":

                st.info(
                    "Nenhuma observação cadastrada."
                )

            else:

                st.write(
                    observacao_cliente
                )

            st.markdown("---")

            st.subheader(
                "🧾 Histórico de Compras"
            )

            conn = conectar()

            historico_vendas = pd.read_sql_query(
                """
                SELECT
                    data AS Data,
                    produto AS Produto,
                    quantidade AS Quantidade,
                    valor_total AS Valor
                FROM vendas
                WHERE LOWER(cliente) = LOWER(?)
                ORDER BY data DESC, id DESC
                """,
                conn,
                params=(nome_cliente,)
            )

            conn.close()

            if historico_vendas.empty:

                st.info(
                    "Ainda não existem compras "
                    "registradas para esta cliente."
                )

            else:

                st.dataframe(
                    historico_vendas,
                    use_container_width=True,
                    hide_index=True
                )

            st.markdown("---")

            st.subheader(
                "📅 Agendamentos da Cliente"
            )

            conn = conectar()

            historico_agenda = pd.read_sql_query(
                """
                SELECT
                    data AS Data,
                    horario AS Horário,
                    servico AS Serviço
                FROM agendamentos
                WHERE LOWER(cliente) = LOWER(?)
                ORDER BY data DESC, horario DESC
                """,
                conn,
                params=(nome_cliente,)
            )

            conn.close()

            if historico_agenda.empty:

                st.info(
                    "Ainda não existem agendamentos "
                    "para esta cliente."
                )

            else:

                st.dataframe(
                    historico_agenda,
                    use_container_width=True,
                    hide_index=True
                )

            # ==================================================
            # HISTÓRICO DE ATENDIMENTOS E COMISSÕES
            # ==================================================
            st.markdown("---")

            st.subheader(
                "💇 Histórico de Atendimentos"
            )

            conn = conectar()

            historico_atendimentos = pd.read_sql_query(
                """
                SELECT
                    data,
                    funcionario_nome,
                    servico,
                    valor_servico,
                    percentual_comissao,
                    valor_comissao,
                    valor_salao,
                    observacao
                FROM atendimentos_comissoes
                WHERE LOWER(cliente) = LOWER(?)
                ORDER BY data DESC, id DESC
                """,
                conn,
                params=(nome_cliente,)
            )

            conn.close()

            if historico_atendimentos.empty:

                st.info(
                    "Ainda não existem atendimentos "
                    "realizados para esta cliente."
                )

            else:

                total_atendimentos = len(
                    historico_atendimentos
                )

                total_servicos = float(
                    historico_atendimentos[
                        "valor_servico"
                    ].sum()
                )

                ultima_visita = (
                    historico_atendimentos.iloc[0][
                        "data"
                    ]
                )

                try:

                    ultima_visita_formatada = (
                        datetime.strptime(
                            str(ultima_visita),
                            "%Y-%m-%d"
                        ).strftime(
                            "%d/%m/%Y"
                        )
                    )

                except (ValueError, TypeError):

                    ultima_visita_formatada = str(
                        ultima_visita
                    )

                coluna_historico1, coluna_historico2, coluna_historico3 = (
                    st.columns(3)
                )

                coluna_historico1.metric(
                    "💇 Atendimentos realizados",
                    total_atendimentos
                )

                coluna_historico2.metric(
                    "💰 Total em serviços",
                    formatar_moeda(
                        total_servicos
                    )
                )

                coluna_historico3.metric(
                    "📅 Última visita",
                    ultima_visita_formatada
                )

                st.markdown("---")

                tabela_atendimentos = (
                    historico_atendimentos.copy()
                )

                tabela_atendimentos[
                    "Data"
                ] = tabela_atendimentos[
                    "data"
                ].apply(
                    lambda valor: (
                        datetime.strptime(
                            str(valor),
                            "%Y-%m-%d"
                        ).strftime(
                            "%d/%m/%Y"
                        )
                        if valor
                        else ""
                    )
                )

                tabela_atendimentos[
                    "Valor do Serviço"
                ] = tabela_atendimentos[
                    "valor_servico"
                ].apply(
                    formatar_moeda
                )

                tabela_atendimentos[
                    "Comissão (%)"
                ] = tabela_atendimentos[
                    "percentual_comissao"
                ].apply(
                    lambda valor: (
                        f"{float(valor):.2f}%"
                    )
                )

                tabela_atendimentos[
                    "Valor da Comissão"
                ] = tabela_atendimentos[
                    "valor_comissao"
                ].apply(
                    formatar_moeda
                )

                tabela_atendimentos[
                    "Valor do Salão"
                ] = tabela_atendimentos[
                    "valor_salao"
                ].apply(
                    formatar_moeda
                )

                tabela_atendimentos = (
                    tabela_atendimentos.rename(
                        columns={
                            "funcionario_nome":
                                "Funcionária",
                            "servico":
                                "Serviço",
                            "observacao":
                                "Observações"
                        }
                    )
                )

                st.dataframe(
                    tabela_atendimentos[
                        [
                            "Data",
                            "Funcionária",
                            "Serviço",
                            "Valor do Serviço",
                            "Comissão (%)",
                            "Valor da Comissão",
                            "Valor do Salão",
                            "Observações"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )
    # ==================================================
    # EDITAR CLIENTE
    # ==================================================
    with aba4:

        st.subheader(
            "✏️ Editar Cliente"
        )

        clientes_df = carregar_clientes()

        if clientes_df.empty:

            st.info(
                "Ainda não existem clientes cadastradas."
            )

        else:

            clientes_df["opcao"] = (
                clientes_df["id"].astype(str)
                + " - "
                + clientes_df["nome"]
            )

            cliente_escolhida = st.selectbox(
                "Escolha a cliente",
                clientes_df["opcao"].tolist(),
                key="editar_cliente"
            )

            cliente_id = int(
                cliente_escolhida
                .split(" - ")[0]
            )

            cliente = clientes_df[
                clientes_df["id"]
                == cliente_id
            ].iloc[0]

            coluna1, coluna2 = st.columns(2)

            with coluna1:

                novo_nome = st.text_input(
                    "Nome completo",
                    value=texto_seguro(
                        cliente["nome"]
                    ),
                    key="edit_nome"
                )

                novo_telefone = st.text_input(
                    "WhatsApp",
                    value=texto_seguro(
                        cliente["telefone"]
                    ),
                    key="edit_telefone"
                )

                novo_email = st.text_input(
                    "E-mail",
                    value=texto_seguro(
                        cliente.get("email")
                    ),
                    key="edit_email"
                )

                novo_instagram = st.text_input(
                    "Instagram",
                    value=texto_seguro(
                        cliente.get("instagram")
                    ),
                    key="edit_instagram"
                )

            with coluna2:

                nova_data = st.date_input(
                    "Data de nascimento",
                    value=data_segura(
                        cliente.get(
                            "nascimento"
                        )
                    ),
                    format="DD/MM/YYYY",
                    key="edit_nascimento"
                )

                novo_endereco = st.text_input(
                    "Endereço",
                    value=texto_seguro(
                        cliente.get(
                            "endereco"
                        )
                    ),
                    key="edit_endereco"
                )

                servico_atual = texto_seguro(
                    cliente.get(
                        "servico_favorito"
                    )
                )

                if (
                    servico_atual
                    in LISTA_SERVICOS
                ):

                    indice_servico = (
                        LISTA_SERVICOS.index(
                            servico_atual
                        )
                    )

                else:

                    indice_servico = 0

                novo_servico = st.selectbox(
                    "Serviço favorito",
                    LISTA_SERVICOS,
                    index=indice_servico,
                    key="edit_servico"
                )

                nova_foto = st.file_uploader(
                    "Alterar foto",
                    type=[
                        "png",
                        "jpg",
                        "jpeg"
                    ],
                    key="edit_foto"
                )

            nova_observacao = st.text_area(
                "Observações",
                value=texto_seguro(
                    cliente.get(
                        "observacao"
                    )
                ),
                key="edit_observacao"
            )

            if st.button(
                "💾 Salvar Alterações",
                use_container_width=True,
                key="btn_editar_cliente"
            ):

                if novo_nome.strip() == "":

                    st.error(
                        "O nome não pode ficar vazio."
                    )

                else:

                    foto_atual = texto_seguro(
                        cliente.get(
                            "foto"
                        )
                    )

                    if nova_foto is not None:

                        caminho_foto = salvar_foto(
                            nova_foto,
                            novo_nome
                        )

                    else:

                        caminho_foto = foto_atual

                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        UPDATE clientes
                        SET
                            nome = ?,
                            telefone = ?,
                            servico = ?,
                            observacao = ?,
                            email = ?,
                            instagram = ?,
                            nascimento = ?,
                            endereco = ?,
                            servico_favorito = ?,
                            foto = ?
                        WHERE id = ?
                        """,
                        (
                            novo_nome.strip(),
                            novo_telefone.strip(),
                            novo_servico,
                            nova_observacao.strip(),
                            novo_email.strip(),
                            novo_instagram.strip(),
                            str(nova_data),
                            novo_endereco.strip(),
                            novo_servico,
                            caminho_foto,
                            cliente_id
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "Cliente atualizada "
                        "com sucesso!"
                    )

                    st.rerun()

    # ==================================================
    # EXCLUIR CLIENTE
    # ==================================================
    with aba5:

        st.subheader(
            "🗑️ Excluir Cliente"
        )

        clientes_df = carregar_clientes()

        if clientes_df.empty:

            st.info(
                "Ainda não existem clientes cadastradas."
            )

        else:

            clientes_df["opcao"] = (
                clientes_df["id"].astype(str)
                + " - "
                + clientes_df["nome"]
            )

            cliente_excluir = st.selectbox(
                "Escolha a cliente para excluir",
                clientes_df["opcao"].tolist(),
                key="excluir_cliente"
            )

            excluir_id = int(
                cliente_excluir
                .split(" - ")[0]
            )

            cliente = clientes_df[
                clientes_df["id"]
                == excluir_id
            ].iloc[0]

            nome_excluir = texto_seguro(
                cliente["nome"]
            )

            st.warning(
                f"Você está prestes a excluir: "
                f"{nome_excluir}"
            )

            confirmar = st.checkbox(
                "Confirmo que desejo excluir "
                "esta cliente",
                key="confirmar_exclusao_cliente"
            )

            if st.button(
                "🗑️ Excluir Cliente",
                use_container_width=True,
                key="btn_excluir_cliente"
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
                        DELETE FROM clientes
                        WHERE id = ?
                        """,
                        (excluir_id,)
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        f"Cliente {nome_excluir} "
                        "excluída com sucesso!"
                    )

                    st.rerun()

    # ==================================================
    # LISTA GERAL
    # ==================================================
    st.markdown("---")

    st.subheader(
        "📋 Clientes Cadastradas"
    )

    lista_clientes = carregar_clientes()

    if lista_clientes.empty:

        st.info(
            "Ainda não existem clientes cadastradas."
        )

    else:

        colunas_lista = [
            "id",
            "nome",
            "telefone",
            "email",
            "instagram",
            "nascimento",
            "servico_favorito"
        ]

        colunas_existentes = [
            coluna
            for coluna in colunas_lista
            if coluna in lista_clientes.columns
        ]

        st.dataframe(
            lista_clientes[
                colunas_existentes
            ],
            use_container_width=True,
            hide_index=True
        )

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

PASTA_ANTES_DEPOIS = (
    PASTA_PROJETO
    / "assets"
    / "imagens"
    / "antes_depois"
)

PASTA_ANTES_DEPOIS.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# FUNÇÕES AUXILIARES
# ==================================================
def nome_arquivo_seguro(texto):

    texto_normalizado = unicodedata.normalize(
        "NFKD",
        str(texto)
    )

    texto_sem_acentos = "".join(
        caractere
        for caractere in texto_normalizado
        if not unicodedata.combining(caractere)
    )

    texto_limpo = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        texto_sem_acentos
    )

    return texto_limpo.lower()


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


def salvar_imagem(
    arquivo,
    cliente,
    tipo_foto
):

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

    nome_cliente = nome_arquivo_seguro(
        cliente
    )

    momento = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    nome_arquivo = (
        f"{nome_cliente}_"
        f"{tipo_foto}_"
        f"{momento}"
        f"{extensao}"
    )

    caminho = (
        PASTA_ANTES_DEPOIS
        / nome_arquivo
    )

    with open(
        caminho,
        "wb"
    ) as destino:

        destino.write(
            arquivo.getbuffer()
        )

    return str(caminho)


# ==================================================
# CRIAR TABELA
# ==================================================
def criar_tabela_antes_depois():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS antes_depois (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            servico TEXT NOT NULL,
            funcionario TEXT,
            data TEXT NOT NULL,
            foto_antes TEXT,
            foto_depois TEXT,
            observacao TEXT
        )
        """
    )

    conn.commit()
    conn.close()


# ==================================================
# CARREGAR CLIENTES
# ==================================================
def carregar_clientes():

    conn = conectar()

    clientes_df = pd.read_sql_query(
        """
        SELECT
            id,
            nome
        FROM clientes
        ORDER BY nome
        """,
        conn
    )

    conn.close()

    return clientes_df


# ==================================================
# CARREGAR SERVIÇOS
# ==================================================
def carregar_servicos():

    conn = conectar()

    servicos_df = pd.read_sql_query(
        """
        SELECT
            id,
            nome
        FROM servicos_catalogo
        WHERE ativo = 1
        ORDER BY nome
        """,
        conn
    )

    conn.close()

    return servicos_df


# ==================================================
# CARREGAR FUNCIONÁRIOS
# ==================================================
def carregar_funcionarios():

    conn = conectar()

    funcionarios_df = pd.read_sql_query(
        """
        SELECT
            id,
            nome
        FROM funcionarios
        WHERE ativo = 1
        ORDER BY nome
        """,
        conn
    )

    conn.close()

    return funcionarios_df


# ==================================================
# CARREGAR REGISTROS
# ==================================================
def carregar_registros():

    criar_tabela_antes_depois()

    conn = conectar()

    registros_df = pd.read_sql_query(
        """
        SELECT *
        FROM antes_depois
        ORDER BY data DESC, id DESC
        """,
        conn
    )

    conn.close()

    return registros_df


# ==================================================
# PÁGINA
# ==================================================
def mostrar_antes_depois():

    criar_tabela_antes_depois()

    st.title(
        "📸 Antes e Depois"
    )

    st.caption(
        "Registre e acompanhe os resultados "
        "dos procedimentos realizados."
    )

    aba1, aba2, aba3 = st.tabs(
        [
            "➕ Novo Registro",
            "🖼️ Galeria",
            "🗑️ Excluir"
        ]
    )

    # ==================================================
    # NOVO REGISTRO
    # ==================================================
    with aba1:

        st.subheader(
            "➕ Registrar Antes e Depois"
        )

        clientes_df = carregar_clientes()
        servicos_df = carregar_servicos()
        funcionarios_df = carregar_funcionarios()

        if clientes_df.empty:

            st.warning(
                "Cadastre pelo menos uma cliente."
            )

        elif servicos_df.empty:

            st.warning(
                "Cadastre pelo menos um serviço ativo."
            )

        else:

            cliente = st.selectbox(
                "Cliente",
                clientes_df["nome"].tolist(),
                key="antes_depois_cliente"
            )

            servico = st.selectbox(
                "Serviço realizado",
                servicos_df["nome"].tolist(),
                key="antes_depois_servico"
            )

            if funcionarios_df.empty:

                funcionario = ""

                st.info(
                    "Nenhuma funcionária ativa cadastrada."
                )

            else:

                funcionario = st.selectbox(
                    "Funcionária responsável",
                    funcionarios_df["nome"].tolist(),
                    key="antes_depois_funcionario"
                )

            data_registro = st.date_input(
                "Data do procedimento",
                value=date.today(),
                format="DD/MM/YYYY",
                key="antes_depois_data"
            )

            coluna1, coluna2 = st.columns(2)

            with coluna1:

                foto_antes = st.file_uploader(
                    "📷 Foto antes",
                    type=[
                        "png",
                        "jpg",
                        "jpeg"
                    ],
                    key="foto_antes"
                )

                if foto_antes is not None:

                    st.image(
                        foto_antes,
                        caption="Foto antes",
                        use_container_width=True
                    )

            with coluna2:

                foto_depois = st.file_uploader(
                    "📷 Foto depois",
                    type=[
                        "png",
                        "jpg",
                        "jpeg"
                    ],
                    key="foto_depois"
                )

                if foto_depois is not None:

                    st.image(
                        foto_depois,
                        caption="Foto depois",
                        use_container_width=True
                    )

            observacao = st.text_area(
                "Observações",
                placeholder=(
                    "Exemplo: técnica utilizada, "
                    "produto aplicado ou cuidados indicados."
                ),
                key="antes_depois_observacao"
            )

            if st.button(
                "💾 Salvar Antes e Depois",
                use_container_width=True,
                key="btn_salvar_antes_depois"
            ):

                if foto_antes is None and foto_depois is None:

                    st.error(
                        "Envie pelo menos uma foto."
                    )

                else:

                    caminho_antes = salvar_imagem(
                        foto_antes,
                        cliente,
                        "antes"
                    )

                    caminho_depois = salvar_imagem(
                        foto_depois,
                        cliente,
                        "depois"
                    )

                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT INTO antes_depois
                        (
                            cliente,
                            servico,
                            funcionario,
                            data,
                            foto_antes,
                            foto_depois,
                            observacao
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            cliente,
                            servico,
                            funcionario,
                            str(data_registro),
                            caminho_antes,
                            caminho_depois,
                            observacao.strip()
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "Registro salvo com sucesso!"
                    )

                    st.rerun()

    # ==================================================
    # GALERIA
    # ==================================================
    with aba2:

        st.subheader(
            "🖼️ Galeria de Resultados"
        )

        registros_df = carregar_registros()

        if registros_df.empty:

            st.info(
                "Ainda não existem registros."
            )

        else:

            clientes = (
                registros_df["cliente"]
                .dropna()
                .unique()
                .tolist()
            )

            cliente_filtro = st.selectbox(
                "Filtrar por cliente",
                [
                    "Todas"
                ] + clientes,
                key="galeria_cliente"
            )

            resultado_df = registros_df.copy()

            if cliente_filtro != "Todas":

                resultado_df = resultado_df[
                    resultado_df["cliente"]
                    == cliente_filtro
                ]

            for _, registro in resultado_df.iterrows():

                with st.container(
                    border=True
                ):

                    st.subheader(
                        f"👩 {registro['cliente']}"
                    )

                    st.write(
                        f"💇 **Serviço:** "
                        f"{registro['servico']}"
                    )

                    st.write(
                        f"👩‍💼 **Funcionária:** "
                        f"{registro['funcionario'] or 'Não informada'}"
                    )

                    st.write(
                        f"📅 **Data:** "
                        f"{formatar_data_br(registro['data'])}"
                    )

                    coluna1, coluna2 = st.columns(2)

                    with coluna1:

                        caminho_antes = str(
                            registro["foto_antes"] or ""
                        )

                        if (
                            caminho_antes != ""
                            and Path(caminho_antes).exists()
                        ):

                            st.image(
                                caminho_antes,
                                caption="Antes",
                                use_container_width=True
                            )

                        else:

                            st.info(
                                "Sem foto antes."
                            )

                    with coluna2:

                        caminho_depois = str(
                            registro["foto_depois"] or ""
                        )

                        if (
                            caminho_depois != ""
                            and Path(caminho_depois).exists()
                        ):

                            st.image(
                                caminho_depois,
                                caption="Depois",
                                use_container_width=True
                            )

                        else:

                            st.info(
                                "Sem foto depois."
                            )

                    observacao = str(
                        registro["observacao"] or ""
                    )

                    if observacao != "":

                        st.write(
                            f"📝 **Observações:** "
                            f"{observacao}"
                        )

    # ==================================================
    # EXCLUIR
    # ==================================================
    with aba3:

        st.subheader(
            "🗑️ Excluir Registro"
        )

        registros_df = carregar_registros()

        if registros_df.empty:

            st.info(
                "Ainda não existem registros para excluir."
            )

        else:

            registros_df["opcao"] = (
                registros_df["id"].astype(str)
                + " - "
                + registros_df["cliente"]
                + " - "
                + registros_df["servico"]
                + " - "
                + registros_df["data"].apply(
                    formatar_data_br
                )
            )

            escolhido = st.selectbox(
                "Escolha o registro",
                registros_df["opcao"].tolist(),
                key="excluir_antes_depois"
            )

            registro_id = int(
                escolhido.split(" - ")[0]
            )

            registro = registros_df[
                registros_df["id"]
                == registro_id
            ].iloc[0]

            st.warning(
                f"Você está prestes a excluir "
                f"o registro de {registro['cliente']}."
            )

            confirmar = st.checkbox(
                "Confirmo que desejo excluir",
                key="confirmar_excluir_antes_depois"
            )

            if st.button(
                "🗑️ Excluir Registro",
                use_container_width=True,
                key="btn_excluir_antes_depois"
            ):

                if not confirmar:

                    st.error(
                        "Marque a confirmação antes de excluir."
                    )

                else:

                    for coluna in [
                        "foto_antes",
                        "foto_depois"
                    ]:

                        caminho = str(
                            registro[coluna] or ""
                        )

                        if (
                            caminho != ""
                            and Path(caminho).exists()
                        ):

                            try:

                                Path(caminho).unlink()

                            except OSError:

                                pass

                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        DELETE FROM antes_depois
                        WHERE id = ?
                        """,
                        (
                            registro_id,
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "Registro excluído com sucesso!"
                    )

                    st.rerun()

    st.markdown("---")

    st.caption(
        "BeautyFlow CRM • "
        "Desenvolvido por "
        "Luciana Oliveira de Albuquerque"
    )

from urllib.parse import quote

import pandas as pd
import streamlit as st

from banco import conectar


# ==================================================
# WHATSAPP DO ESTABELECIMENTO
# ==================================================
WHATSAPP = "5521988219493"


# ==================================================
# SERVIÇOS INICIAIS
# Comissão padrão pode ser alterada depois.
# ==================================================
SERVICOS_INICIAIS = [
    (
        "Extensão de Cílios",
        "Extensão de Cílios",
        120.00,
        40.00
    ),
    (
        "Extensão de Cílios",
        "Manutenção de Cílios",
        80.00,
        40.00
    ),
    (
        "Mechas",
        "Balayagem",
        250.00,
        50.00
    ),
    (
        "Mechas",
        "Strong",
        280.00,
        50.00
    ),
    (
        "Mechas",
        "Morena Iluminada",
        300.00,
        50.00
    ),
    (
        "Mechas",
        "Retoque de Mechas",
        180.00,
        50.00
    ),
    (
        "Cabelo",
        "Corte de Cabelo",
        60.00,
        40.00
    ),
    (
        "Cabelo",
        "Escova Curta",
        50.00,
        30.00
    ),
    (
        "Cabelo",
        "Escova Média",
        70.00,
        30.00
    ),
    (
        "Cabelo",
        "Escova Longa",
        90.00,
        30.00
    ),
    (
        "Tratamentos",
        "Hidratação",
        80.00,
        40.00
    ),
    (
        "Tratamentos",
        "Reconstrução",
        100.00,
        40.00
    ),
    (
        "Tratamentos",
        "Nutrição",
        90.00,
        40.00
    ),
    (
        "Tratamentos",
        "Progressiva sem Formol",
        180.00,
        40.00
    ),
    (
        "Tratamentos",
        "Botox",
        150.00,
        40.00
    ),
    (
        "Micropigmentação",
        "Micropigmentação Esfumada",
        350.00,
        50.00
    ),
    (
        "Micropigmentação",
        "Micropigmentação Fio a Fio",
        400.00,
        50.00
    )
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


def formatar_percentual(valor):

    return f"{float(valor):.2f}%"


# ==================================================
# LINK DO WHATSAPP
# ==================================================
def link_whatsapp(servico, valor):

    valor_formatado = formatar_moeda(
        valor
    )

    mensagem = (
        "Olá, Luciana! Tenho interesse em agendar "
        f"o serviço: {servico}. "
        f"Valor: {valor_formatado}."
    )

    return (
        f"https://wa.me/{WHATSAPP}"
        f"?text={quote(mensagem)}"
    )


# ==================================================
# CRIAR E ATUALIZAR TABELA
# ==================================================
def criar_tabela_servicos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS servicos_catalogo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            nome TEXT NOT NULL,
            valor REAL NOT NULL DEFAULT 0,
            comissao_padrao REAL NOT NULL DEFAULT 0,
            ativo INTEGER NOT NULL DEFAULT 1,
            UNIQUE(categoria, nome)
        )
        """
    )

    # Verifica as colunas que já existem
    cursor.execute(
        "PRAGMA table_info(servicos_catalogo)"
    )

    colunas_existentes = [
        coluna[1]
        for coluna in cursor.fetchall()
    ]

    # Adiciona comissão padrão sem apagar os serviços
    if "comissao_padrao" not in colunas_existentes:

        cursor.execute(
            """
            ALTER TABLE servicos_catalogo
            ADD COLUMN comissao_padrao
            REAL NOT NULL DEFAULT 0
            """
        )

    # Adiciona status ativo/inativo
    if "ativo" not in colunas_existentes:

        cursor.execute(
            """
            ALTER TABLE servicos_catalogo
            ADD COLUMN ativo
            INTEGER NOT NULL DEFAULT 1
            """
        )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM servicos_catalogo
        """
    )

    quantidade = cursor.fetchone()[0]

    # Só adiciona a lista inicial se a tabela estiver vazia
    if quantidade == 0:

        cursor.executemany(
            """
            INSERT OR IGNORE INTO servicos_catalogo
            (
                categoria,
                nome,
                valor,
                comissao_padrao,
                ativo
            )
            VALUES (?, ?, ?, ?, 1)
            """,
            SERVICOS_INICIAIS
        )

    conn.commit()
    conn.close()


# ==================================================
# CARREGAR SERVIÇOS
# ==================================================
def carregar_servicos(
    apenas_ativos=False
):

    criar_tabela_servicos()

    conn = conectar()

    if apenas_ativos:

        servicos_df = pd.read_sql_query(
            """
            SELECT
                id,
                categoria,
                nome,
                valor,
                comissao_padrao,
                ativo
            FROM servicos_catalogo
            WHERE ativo = 1
            ORDER BY categoria, nome
            """,
            conn
        )

    else:

        servicos_df = pd.read_sql_query(
            """
            SELECT
                id,
                categoria,
                nome,
                valor,
                comissao_padrao,
                ativo
            FROM servicos_catalogo
            ORDER BY categoria, nome
            """,
            conn
        )

    conn.close()

    return servicos_df


# ==================================================
# PÁGINA SERVIÇOS
# ==================================================
def mostrar_servicos():

    criar_tabela_servicos()

    st.title(
        "💅 Serviços e Valores"
    )

    st.caption(
        "Cadastre serviços, altere preços, "
        "defina a comissão padrão e controle "
        "quais serviços estão ativos."
    )

    aba1, aba2, aba3, aba4 = st.tabs(
        [
            "💅 Ver Serviços",
            "➕ Novo Serviço",
            "✏️ Editar Serviço",
            "🗑️ Excluir"
        ]
    )

    # ==================================================
    # VER SERVIÇOS
    # ==================================================
    with aba1:

        st.subheader(
            "💅 Catálogo de Serviços"
        )

        mostrar_inativos = st.checkbox(
            "Mostrar também serviços inativos",
            value=False,
            key="mostrar_servicos_inativos"
        )

        servicos_df = carregar_servicos(
            apenas_ativos=not mostrar_inativos
        )

        if servicos_df.empty:

            st.info(
                "Ainda não existem serviços cadastrados."
            )

        else:

            categorias = (
                servicos_df["categoria"]
                .dropna()
                .unique()
                .tolist()
            )

            categoria_escolhida = st.selectbox(
                "Escolha uma categoria",
                categorias,
                key="categoria_visualizar"
            )

            servicos_categoria = servicos_df[
                servicos_df["categoria"]
                == categoria_escolhida
            ]

            for _, servico in servicos_categoria.iterrows():

                st.subheader(
                    str(servico["nome"])
                )

                coluna_valor, coluna_comissao = st.columns(
                    2
                )

                with coluna_valor:

                    st.metric(
                        "💰 Valor padrão",
                        formatar_moeda(
                            servico["valor"]
                        )
                    )

                with coluna_comissao:

                    st.metric(
                        "👩‍💼 Comissão padrão",
                        formatar_percentual(
                            servico[
                                "comissao_padrao"
                            ]
                        )
                    )

                status = (
                    "🟢 Ativo"
                    if int(servico["ativo"]) == 1
                    else "🔴 Inativo"
                )

                st.write(
                    f"**Status:** {status}"
                )

                if int(servico["ativo"]) == 1:

                    link = link_whatsapp(
                        str(servico["nome"]),
                        float(servico["valor"])
                    )

                    st.link_button(
                        "💬 Agendar pelo WhatsApp",
                        link,
                        use_container_width=True
                    )

                st.markdown("---")

    # ==================================================
    # NOVO SERVIÇO
    # ==================================================
    with aba2:

        st.subheader(
            "➕ Cadastrar Novo Serviço"
        )

        coluna1, coluna2 = st.columns(
            2
        )

        with coluna1:

            categoria_nova = st.text_input(
                "Categoria",
                placeholder=(
                    "Exemplo: Cabelo, Unhas, "
                    "Estética Facial"
                ),
                key="novo_servico_categoria"
            )

            nome_novo = st.text_input(
                "Nome do serviço",
                placeholder=(
                    "Exemplo: Limpeza de Pele"
                ),
                key="novo_servico_nome"
            )

        with coluna2:

            valor_novo = st.number_input(
                "Valor padrão do serviço (R$)",
                min_value=0.0,
                step=10.0,
                format="%.2f",
                key="novo_servico_valor"
            )

            comissao_nova = st.number_input(
                "Comissão padrão da funcionária (%)",
                min_value=0.0,
                max_value=100.0,
                step=5.0,
                format="%.2f",
                key="novo_servico_comissao"
            )

        ativo_novo = st.checkbox(
            "Serviço ativo",
            value=True,
            key="novo_servico_ativo"
        )

        st.info(
            "A comissão padrão será sugerida no "
            "atendimento, mas poderá ser alterada "
            "antes de salvar."
        )

        if st.button(
            "💾 Salvar Novo Serviço",
            use_container_width=True,
            key="btn_salvar_novo_servico"
        ):

            if categoria_nova.strip() == "":

                st.error(
                    "Digite a categoria."
                )

            elif nome_novo.strip() == "":

                st.error(
                    "Digite o nome do serviço."
                )

            elif valor_novo <= 0:

                st.error(
                    "O valor deve ser maior que zero."
                )

            elif comissao_nova < 0:

                st.error(
                    "A comissão não pode ser negativa."
                )

            else:

                conn = conectar()
                cursor = conn.cursor()

                try:

                    cursor.execute(
                        """
                        INSERT INTO servicos_catalogo
                        (
                            categoria,
                            nome,
                            valor,
                            comissao_padrao,
                            ativo
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            categoria_nova.strip(),
                            nome_novo.strip(),
                            float(valor_novo),
                            float(comissao_nova),
                            1 if ativo_novo else 0
                        )
                    )

                    conn.commit()

                    st.success(
                        "Novo serviço cadastrado "
                        "com sucesso!"
                    )

                    st.rerun()

                except Exception:

                    st.error(
                        "Esse serviço já está cadastrado "
                        "nessa categoria."
                    )

                finally:

                    conn.close()

    # ==================================================
    # EDITAR SERVIÇO
    # ==================================================
    with aba3:

        st.subheader(
            "✏️ Editar Serviço"
        )

        servicos_df = carregar_servicos()

        if servicos_df.empty:

            st.info(
                "Ainda não existem serviços cadastrados."
            )

        else:

            servicos_df["opcao"] = (
                servicos_df["id"].astype(str)
                + " - "
                + servicos_df["categoria"]
                + " - "
                + servicos_df["nome"]
                + " - "
                + servicos_df["valor"].apply(
                    formatar_moeda
                )
            )

            servico_escolhido = st.selectbox(
                "Escolha o serviço",
                servicos_df["opcao"].tolist(),
                key="editar_servico_escolhido"
            )

            servico_id = int(
                servico_escolhido.split(" - ")[0]
            )

            linha = servicos_df[
                servicos_df["id"] == servico_id
            ].iloc[0]

            coluna1, coluna2 = st.columns(
                2
            )

            with coluna1:

                nova_categoria = st.text_input(
                    "Categoria",
                    value=str(
                        linha["categoria"]
                    ),
                    key="editar_servico_categoria"
                )

                novo_nome = st.text_input(
                    "Nome do serviço",
                    value=str(
                        linha["nome"]
                    ),
                    key="editar_servico_nome"
                )

            with coluna2:

                novo_valor = st.number_input(
                    "Valor padrão (R$)",
                    min_value=0.0,
                    value=float(
                        linha["valor"]
                    ),
                    step=10.0,
                    format="%.2f",
                    key="editar_servico_valor"
                )

                nova_comissao = st.number_input(
                    "Comissão padrão da funcionária (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(
                        linha["comissao_padrao"]
                    ),
                    step=5.0,
                    format="%.2f",
                    key="editar_servico_comissao"
                )

            novo_ativo = st.checkbox(
                "Serviço ativo",
                value=bool(
                    linha["ativo"]
                ),
                key="editar_servico_ativo"
            )

            st.write(
                f"💰 **Valor:** "
                f"{formatar_moeda(novo_valor)}"
            )

            st.write(
                f"👩‍💼 **Comissão padrão:** "
                f"{formatar_percentual(nova_comissao)}"
            )

            valor_comissao_exemplo = (
                float(novo_valor)
                * float(nova_comissao)
                / 100
            )

            valor_salao_exemplo = (
                float(novo_valor)
                - valor_comissao_exemplo
            )

            exemplo1, exemplo2 = st.columns(
                2
            )

            exemplo1.metric(
                "Exemplo — Funcionária",
                formatar_moeda(
                    valor_comissao_exemplo
                )
            )

            exemplo2.metric(
                "Exemplo — Salão",
                formatar_moeda(
                    valor_salao_exemplo
                )
            )

            if st.button(
                "💾 Salvar Alterações",
                use_container_width=True,
                key="btn_salvar_alteracao_servico"
            ):

                if nova_categoria.strip() == "":

                    st.error(
                        "A categoria não pode ficar vazia."
                    )

                elif novo_nome.strip() == "":

                    st.error(
                        "O nome não pode ficar vazio."
                    )

                elif novo_valor <= 0:

                    st.error(
                        "O valor deve ser maior que zero."
                    )

                else:

                    conn = conectar()
                    cursor = conn.cursor()

                    try:

                        cursor.execute(
                            """
                            UPDATE servicos_catalogo
                            SET
                                categoria = ?,
                                nome = ?,
                                valor = ?,
                                comissao_padrao = ?,
                                ativo = ?
                            WHERE id = ?
                            """,
                            (
                                nova_categoria.strip(),
                                novo_nome.strip(),
                                float(novo_valor),
                                float(nova_comissao),
                                1 if novo_ativo else 0,
                                servico_id
                            )
                        )

                        conn.commit()

                        st.success(
                            "Serviço atualizado "
                            "com sucesso!"
                        )

                        st.rerun()

                    except Exception:

                        st.error(
                            "Já existe outro serviço "
                            "com esse nome nessa categoria."
                        )

                    finally:

                        conn.close()

    # ==================================================
    # EXCLUIR SERVIÇO
    # ==================================================
    with aba4:

        st.subheader(
            "🗑️ Excluir Serviço"
        )

        servicos_df = carregar_servicos()

        if servicos_df.empty:

            st.info(
                "Ainda não existem serviços cadastrados."
            )

        else:

            servicos_df["opcao"] = (
                servicos_df["id"].astype(str)
                + " - "
                + servicos_df["categoria"]
                + " - "
                + servicos_df["nome"]
            )

            servico_excluir = st.selectbox(
                "Escolha o serviço",
                servicos_df["opcao"].tolist(),
                key="excluir_servico_escolhido"
            )

            excluir_id = int(
                servico_excluir.split(" - ")[0]
            )

            linha_excluir = servicos_df[
                servicos_df["id"] == excluir_id
            ].iloc[0]

            st.warning(
                f"Você está prestes a excluir: "
                f"{linha_excluir['nome']} — "
                f"{formatar_moeda(linha_excluir['valor'])}"
            )

            st.info(
                "Se esse serviço já foi usado em "
                "atendimentos, é mais seguro deixá-lo "
                "inativo em vez de excluir."
            )

            confirmar = st.checkbox(
                "Confirmo que desejo excluir "
                "este serviço",
                key="confirmar_exclusao_servico"
            )

            if st.button(
                "🗑️ Excluir Serviço",
                use_container_width=True,
                key="btn_excluir_servico"
            ):

                if not confirmar:

                    st.error(
                        "Marque a confirmação antes "
                        "de excluir."
                    )

                else:

                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        DELETE FROM servicos_catalogo
                        WHERE id = ?
                        """,
                        (excluir_id,)
                    )

                    conn.commit()
                    conn.close()

                    st.success(
                        "Serviço excluído com sucesso!"
                    )

                    st.rerun()

    # ==================================================
    # TABELA GERAL
    # ==================================================
    st.markdown("---")

    st.subheader(
        "📋 Tabela Completa de Serviços"
    )

    tabela_servicos = carregar_servicos()

    if tabela_servicos.empty:

        st.info(
            "Ainda não existem serviços cadastrados."
        )

    else:

        tabela_exibir = tabela_servicos.copy()

        tabela_exibir["Valor"] = tabela_exibir[
            "valor"
        ].apply(
            formatar_moeda
        )

        tabela_exibir[
            "Comissão Padrão"
        ] = tabela_exibir[
            "comissao_padrao"
        ].apply(
            formatar_percentual
        )

        tabela_exibir["Status"] = tabela_exibir[
            "ativo"
        ].apply(
            lambda valor: (
                "Ativo"
                if int(valor) == 1
                else "Inativo"
            )
        )

        tabela_exibir = tabela_exibir.rename(
            columns={
                "categoria": "Categoria",
                "nome": "Serviço"
            }
        )

        st.dataframe(
            tabela_exibir[
                [
                    "Categoria",
                    "Serviço",
                    "Valor",
                    "Comissão Padrão",
                    "Status"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "BeautyFlow CRM • "
        "Desenvolvido por "
        "Luciana Oliveira de Albuquerque"
    )
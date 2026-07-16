from datetime import date, datetime

import pandas as pd
import streamlit as st

from banco import conectar
from pagina.financeiro_auto import registrar_entrada_financeiro

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


# ==================================================
# CRIAR TABELA DE COMISSÕES
# ==================================================
def criar_tabela_comissoes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS atendimentos_comissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER NOT NULL,
            funcionario_nome TEXT NOT NULL,
            cliente TEXT NOT NULL,
            servico TEXT NOT NULL,
            valor_servico REAL NOT NULL,
            percentual_comissao REAL NOT NULL,
            valor_comissao REAL NOT NULL,
            valor_salao REAL NOT NULL,
            data TEXT NOT NULL,
            observacao TEXT,
            FOREIGN KEY (funcionario_id)
                REFERENCES funcionarios(id)
        )
        """
    )

    conn.commit()
    conn.close()


# ==================================================
# CARREGAR FUNCIONÁRIOS ATIVOS
# ==================================================
def carregar_funcionarios_ativos():

    conn = conectar()

    funcionarios_df = pd.read_sql_query(
        """
        SELECT
            id,
            nome,
            funcao
        FROM funcionarios
        WHERE ativo = 1
        ORDER BY nome
        """,
        conn
    )

    conn.close()

    return funcionarios_df


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
            categoria,
            nome,
            valor
        FROM servicos_catalogo
        ORDER BY categoria, nome
        """,
        conn
    )

    conn.close()

    return servicos_df


# ==================================================
# CARREGAR COMISSÕES
# ==================================================
def carregar_comissoes():

    criar_tabela_comissoes()

    conn = conectar()

    comissoes_df = pd.read_sql_query(
        """
        SELECT *
        FROM atendimentos_comissoes
        ORDER BY data DESC, id DESC
        """,
        conn
    )

    conn.close()

    return comissoes_df


# ==================================================
# PÁGINA PRINCIPAL
# ==================================================
def mostrar_comissoes():

    criar_tabela_comissoes()

    st.title("💰 Atendimentos e Comissões")

    st.caption(
        "Registre o serviço realizado e calcule "
        "automaticamente a comissão do funcionário."
    )

    aba1, aba2, aba3, aba4 = st.tabs(
        [
            "➕ Registrar Atendimento",
            "📋 Histórico",
            "📊 Resumo",
            "🗑️ Excluir"
        ]
    )

    # ==================================================
    # REGISTRAR ATENDIMENTO
    # ==================================================
    with aba1:

        st.subheader("➕ Registrar Atendimento")

        funcionarios_df = carregar_funcionarios_ativos()
        clientes_df = carregar_clientes()
        servicos_df = carregar_servicos()

        if funcionarios_df.empty:

            st.warning(
                "Cadastre pelo menos um funcionário ativo."
            )

        elif servicos_df.empty:

            st.warning(
                "Cadastre pelo menos um serviço."
            )

        else:

          
            funcionarios_df["opcao"] = (
                funcionarios_df["nome"]
                + " • "
                + funcionarios_df["funcao"].fillna("")
)

            funcionario_escolhido = st.selectbox(
                "Funcionário",
                funcionarios_df["opcao"].tolist(),
                key="comissao_funcionario"
            )

           
            funcionario_linha = funcionarios_df[
                funcionarios_df["opcao"] == funcionario_escolhido
            ].iloc[0]

            funcionario_id = int(funcionario_linha["id"])

            funcionario_nome = funcionario_linha["nome"]

            funcionario_linha = funcionarios_df[
                funcionarios_df["id"] == funcionario_id
            ].iloc[0]

            funcionario_nome = str(
                funcionario_linha["nome"]
            )

            usar_cliente_cadastrada = st.checkbox(
                "Selecionar cliente cadastrada",
                value=not clientes_df.empty,
                key="comissao_cliente_cadastrada"
            )

            if usar_cliente_cadastrada and not clientes_df.empty:

                cliente = st.selectbox(
                    "Cliente",
                    clientes_df["nome"].tolist(),
                    key="comissao_cliente_lista"
                )

            else:

                cliente = st.text_input(
                    "Nome da cliente",
                    key="comissao_cliente_manual"
                )

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
                "Serviço realizado",
                servicos_df["opcao"].tolist(),
                key="comissao_servico"
            )

            servico_id = int(
                servico_escolhido.split(" - ")[0]
            )

            servico_linha = servicos_df[
                servicos_df["id"] == servico_id
            ].iloc[0]

            servico_nome = str(
                servico_linha["nome"]
            )

            valor_servico = st.number_input(
                "Valor do serviço (R$)",
                min_value=0.0,
                value=float(
                    servico_linha["valor"]
                ),
                step=10.0,
                format="%.2f",
                key="comissao_valor_servico"
            )

            opcao_comissao = st.selectbox(
                "Comissão da funcionária neste atendimento",
                [
                    "20%",
                    "30%",
                    "40%",
                    "50%",
                    "60%",
                    "Outro percentual"
                ],
                index=2,
                key="comissao_opcao_percentual"
            )

            if opcao_comissao == "Outro percentual":

                percentual_comissao = st.number_input(
                    "Digite o percentual da comissão",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    format="%.2f",
                    key="comissao_percentual_outro"
                )

            else:

                percentual_comissao = float(
                    opcao_comissao.replace("%", "")
                )
            
                st.caption(
                    f"A funcionária receberá "
                    f"{percentual_comissao:.0f}% "
                    f"do valor deste serviço."
            )


            data_atendimento = st.date_input(
                "Data do atendimento",
                value=date.today(),
                format="DD/MM/YYYY",
                key="comissao_data"
            )

            observacao = st.text_area(
             "Observações",
                key="comissao_observacao"
            )


            forma_pagamento = st.selectbox(
                "Forma de pagamento",
                [
                   "Pix",
                   "Dinheiro",
                   "Cartão de Débito",
                   "Cartão de Crédito",
                   "Transferência",
                   "Outro"
                ],
                key="comissao_forma_pagamento"
)

            registrar_no_financeiro = st.checkbox(
               "Registrar automaticamente no Financeiro",
               value=True,
               key="registrar_atendimento_financeiro"
)

            valor_comissao = (
                float(valor_servico)
                * float(percentual_comissao)
                / 100
            )

            valor_salao = (
                float(valor_servico)
                - valor_comissao
            )

            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "💵 Valor do serviço",
                formatar_moeda(valor_servico)
            )

            col2.metric(
                "👩‍💼 Comissão do funcionário",
                formatar_moeda(valor_comissao)
            )

            col3.metric(
                "🏢 Valor do salão",
                formatar_moeda(valor_salao)
            )

            if st.button(
                "💾 Salvar Atendimento",
                use_container_width=True,
                key="btn_salvar_comissao"
            ):

                if str(cliente).strip() == "":

                    st.error(
                        "Digite ou selecione a cliente."
                    )

                elif valor_servico <= 0:

                    st.error(
                        "O valor do serviço deve ser maior que zero."
                    )

                elif percentual_comissao <= 0:

                    st.error(
                        "Digite a comissão deste serviço."
                    )

                else:

                    conn = conectar()
                    cursor = conn.cursor()

                    try:

                        cursor.execute(
                            """
                            INSERT INTO atendimentos_comissoes
                            (
                                funcionario_id,
                                funcionario_nome,
                                cliente,
                                servico,
                                valor_servico,
                                percentual_comissao,
                                valor_comissao,
                                valor_salao,
                                data,
                                observacao
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                funcionario_id,
                                funcionario_nome,
                                str(cliente).strip(),
                                servico_nome,
                                float(valor_servico),
                                float(percentual_comissao),
                                float(valor_comissao),
                                float(valor_salao),
                                str(data_atendimento),
                                observacao.strip()
                            )
                        )

                        conn.commit()
                        conn.close()

                        if registrar_no_financeiro:

                            descricao_financeiro = (
                                f"Atendimento - "
                                f"{str(cliente).strip()} - "
                                f"{servico_nome}"
                            )

                            observacao_financeiro = (
                                f"Funcionária: {funcionario_nome}. "
                                f"Comissão: {percentual_comissao:.2f}% "
                                f"({formatar_moeda(valor_comissao)}). "
                                f"Valor do salão: "
                                f"{formatar_moeda(valor_salao)}."
                            )

                            registrar_entrada_financeiro(
                                descricao=descricao_financeiro,
                                valor=float(valor_servico),
                                forma_pagamento=forma_pagamento,
                                data=data_atendimento,
                                observacao=observacao_financeiro
                            )

                            st.success(
                                "Atendimento salvo e entrada "
                                "registrada no Financeiro!"
                            )

                        else:

                            st.success(
                                "Atendimento e comissão "
                                "salvos com sucesso!"
                            )

                        st.rerun()

                    except Exception as erro:

                        try:
                            conn.rollback()
                            conn.close()
                        except Exception:
                            pass

                        st.error(
                            "Não foi possível salvar o atendimento."
                        )

                        st.code(
                            str(erro)
                        )
    # ==================================================
    # HISTÓRICO
    # ==================================================
    with aba2:

        st.subheader("📋 Histórico de Comissões")

        comissoes_df = carregar_comissoes()

        if comissoes_df.empty:

            st.info(
                "Ainda não existem comissões registradas."
            )

        else:

            busca = st.text_input(
                "Pesquisar funcionário, cliente ou serviço",
                key="buscar_comissao"
            )

            resultado_df = comissoes_df.copy()

            if busca.strip() != "":

                busca_normalizada = busca.strip().lower()

                filtro = (
                    resultado_df["funcionario_nome"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        busca_normalizada,
                        regex=False
                    )
                    |
                    resultado_df["cliente"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        busca_normalizada,
                        regex=False
                    )
                    |
                    resultado_df["servico"]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        busca_normalizada,
                        regex=False
                    )
                )

                resultado_df = resultado_df[
                    filtro
                ]

            tabela = resultado_df.copy()

            tabela["Data"] = tabela["data"].apply(
                formatar_data_br
            )

            tabela["Valor do Serviço"] = tabela[
                "valor_servico"
            ].apply(
                formatar_moeda
            )

            tabela["Comissão (%)"] = tabela[
                "percentual_comissao"
            ].apply(
                lambda valor: f"{float(valor):.2f}%"
            )

            tabela["Valor da Comissão"] = tabela[
                "valor_comissao"
            ].apply(
                formatar_moeda
            )

            tabela["Valor do Salão"] = tabela[
                "valor_salao"
            ].apply(
                formatar_moeda
            )

            tabela = tabela.rename(
                columns={
                    "funcionario_nome": "Funcionário",
                    "cliente": "Cliente",
                    "servico": "Serviço"
                }
            )

            st.dataframe(
                tabela[
                    [
                        "Data",
                        "Funcionário",
                        "Cliente",
                        "Serviço",
                        "Valor do Serviço",
                        "Comissão (%)",
                        "Valor da Comissão",
                        "Valor do Salão"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

    # ==================================================
    # RESUMO
    # ==================================================
    with aba3:

        st.subheader("📊 Resumo de Comissões")

        comissoes_df = carregar_comissoes()

        if comissoes_df.empty:

            st.info(
                "Ainda não existem dados para o resumo."
            )

        else:

            col1, col2, col3 = st.columns(3)

            total_servicos = float(
                comissoes_df["valor_servico"].sum()
            )

            total_comissoes = float(
                comissoes_df["valor_comissao"].sum()
            )

            total_salao = float(
                comissoes_df["valor_salao"].sum()
            )

            col1.metric(
                "💵 Total em serviços",
                formatar_moeda(total_servicos)
            )

            col2.metric(
                "👩‍💼 Total de comissões",
                formatar_moeda(total_comissoes)
            )

            col3.metric(
                "🏢 Total do salão",
                formatar_moeda(total_salao)
            )

            st.markdown("---")

            st.subheader(
                "👩‍💼 Comissão por Funcionário"
            )

            resumo_funcionarios = (
                comissoes_df
                .groupby("funcionario_nome")
                .agg(
                    Atendimentos=("id", "count"),
                    Total_Servicos=(
                        "valor_servico",
                        "sum"
                    ),
                    Total_Comissao=(
                        "valor_comissao",
                        "sum"
                    ),
                    Total_Salao=(
                        "valor_salao",
                        "sum"
                    )
                )
                .reset_index()
            )

            resumo_funcionarios[
                "Total Serviços"
            ] = resumo_funcionarios[
                "Total_Servicos"
            ].apply(
                formatar_moeda
            )

            resumo_funcionarios[
                "Total Comissão"
            ] = resumo_funcionarios[
                "Total_Comissao"
            ].apply(
                formatar_moeda
            )

            resumo_funcionarios[
                "Total Salão"
            ] = resumo_funcionarios[
                "Total_Salao"
            ].apply(
                formatar_moeda
            )

            resumo_funcionarios = resumo_funcionarios.rename(
                columns={
                    "funcionario_nome": "Funcionário"
                }
            )

            st.dataframe(
                resumo_funcionarios[
                    [
                        "Funcionário",
                        "Atendimentos",
                        "Total Serviços",
                        "Total Comissão",
                        "Total Salão"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.bar_chart(
                resumo_funcionarios.set_index(
                    "Funcionário"
                )["Total_Comissao"]
            )

    # ==================================================
    # EXCLUIR
    # ==================================================
    with aba4:

        st.subheader("🗑️ Excluir Registro")

        comissoes_df = carregar_comissoes()

        if comissoes_df.empty:

            st.info(
                "Ainda não existem registros para excluir."
            )

        else:

            comissoes_df["opcao"] = (
                comissoes_df["id"].astype(str)
                + " - "
                + comissoes_df["funcionario_nome"]
                + " - "
                + comissoes_df["cliente"]
                + " - "
                + comissoes_df["servico"]
                + " - "
                + comissoes_df["data"].apply(
                    formatar_data_br
                )
            )

            escolhido_excluir = st.selectbox(
                "Escolha o registro",
                comissoes_df["opcao"].tolist(),
                key="excluir_comissao"
            )

            excluir_id = int(
                escolhido_excluir.split(" - ")[0]
            )

            registro = comissoes_df[
                comissoes_df["id"] == excluir_id
            ].iloc[0]

            st.warning(
                f"Você está prestes a excluir o atendimento "
                f"de {registro['cliente']} realizado por "
                f"{registro['funcionario_nome']}."
            )

            confirmar = st.checkbox(
                "Confirmo que desejo excluir este registro",
                key="confirmar_excluir_comissao"
            )

            if st.button(
                "🗑️ Excluir Registro",
                use_container_width=True,
                key="btn_excluir_comissao"
            ):

                if not confirmar:

                    st.error(
                        "Marque a confirmação antes de excluir."
                    )

                else:

                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        DELETE FROM atendimentos_comissoes
                        WHERE id = ?
                        """,
                        (excluir_id,)
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
        "Desenvolvido por Luciana Oliveira de Albuquerque"
    )
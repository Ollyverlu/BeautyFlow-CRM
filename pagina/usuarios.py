import streamlit as st
import pandas as pd
from banco import conectar


def mostrar_usuarios():

    st.title("👥 Gestão de Usuários")

    st.info(
        "Área exclusiva do Administrador para gerenciar acessos ao CRM."
    )

    aba1, aba2, aba3 = st.tabs([
        "➕ Cadastrar",
        "📋 Visualizar",
        "🗑️ Excluir"
    ])

    # ==================================================
    # CADASTRAR USUÁRIO
    # ==================================================
    with aba1:

        st.subheader("➕ Cadastrar Novo Usuário")

        novo_usuario = st.text_input(
            "Nome de usuário",
            key="novo_usuario"
        )

        nova_senha = st.text_input(
            "Senha",
            type="password",
            key="nova_senha"
        )

        confirmar_senha = st.text_input(
            "Confirmar senha",
            type="password",
            key="confirmar_senha"
        )

        nivel = st.selectbox(
            "Nível de acesso",
            [
                "Administrador",
                "Funcionário"
            ],
            key="nivel_usuario"
        )

        if st.button(
            "💾 Salvar Usuário",
            key="btn_salvar_usuario"
        ):

            if novo_usuario.strip() == "":

                st.error(
                    "Digite o nome do usuário."
                )

            elif nova_senha.strip() == "":

                st.error(
                    "Digite uma senha."
                )

            elif nova_senha != confirmar_senha:

                st.error(
                    "As senhas não são iguais."
                )

            else:

                conn = conectar()
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT id FROM usuarios WHERE usuario = ?",
                    (novo_usuario,)
                )

                usuario_existente = cursor.fetchone()

                if usuario_existente:

                    st.error(
                        "Este nome de usuário já existe."
                    )

                    conn.close()

                else:

                    cursor.execute("""
                        INSERT INTO usuarios
                        (
                            usuario,
                            senha,
                            nivel
                        )
                        VALUES (?, ?, ?)
                    """, (
                        novo_usuario,
                        nova_senha,
                        nivel
                    ))

                    conn.commit()
                    conn.close()

                    st.success(
                        f"Usuário {novo_usuario} cadastrado com sucesso!"
                    )

                    st.rerun()

    # ==================================================
    # VISUALIZAR USUÁRIOS
    # ==================================================
    with aba2:

        st.subheader("📋 Usuários Cadastrados")

        conn = conectar()

        usuarios_df = pd.read_sql_query("""
            SELECT
                id,
                usuario,
                nivel
            FROM usuarios
            ORDER BY id
        """, conn)

        conn.close()

        if usuarios_df.empty:

            st.info(
                "Ainda não existem usuários cadastrados."
            )

        else:

            st.dataframe(
                usuarios_df,
                use_container_width=True
            )

    # ==================================================
    # EXCLUIR USUÁRIO
    # ==================================================
    with aba3:

        st.subheader("🗑️ Excluir Usuário")

        conn = conectar()

        usuarios_excluir_df = pd.read_sql_query("""
            SELECT
                id,
                usuario,
                nivel
            FROM usuarios
            ORDER BY usuario
        """, conn)

        conn.close()

        if usuarios_excluir_df.empty:

            st.info(
                "Ainda não existem usuários cadastrados."
            )

        else:

            usuarios_excluir_df["opcao"] = (
                usuarios_excluir_df["id"].astype(str)
                + " - "
                + usuarios_excluir_df["usuario"]
                + " - "
                + usuarios_excluir_df["nivel"]
            )

            usuario_escolhido = st.selectbox(
                "Escolha o usuário para excluir",
                usuarios_excluir_df["opcao"].tolist(),
                key="excluir_usuario"
            )

            usuario_id = int(
                usuario_escolhido.split(" - ")[0]
            )

            linha_usuario = usuarios_excluir_df[
                usuarios_excluir_df["id"] == usuario_id
            ].iloc[0]

            nome_usuario = linha_usuario["usuario"]

            st.warning(
                f"Você está prestes a excluir o usuário: {nome_usuario}"
            )

            if nome_usuario == "admin":

                st.error(
                    "O usuário principal admin não pode ser excluído."
                )

            else:

                confirmar = st.checkbox(
                    "Confirmo que desejo excluir este usuário",
                    key="confirmar_exclusao_usuario"
                )

                if st.button(
                    "🗑️ Excluir Usuário",
                    key="btn_excluir_usuario"
                ):

                    if not confirmar:

                        st.error(
                            "Marque a confirmação antes de excluir."
                        )

                    else:

                        conn = conectar()
                        cursor = conn.cursor()

                        cursor.execute(
                            "DELETE FROM usuarios WHERE id = ?",
                            (usuario_id,)
                        )

                        conn.commit()
                        conn.close()

                        st.success(
                            f"Usuário {nome_usuario} excluído com sucesso!"
                        )

                        st.rerun()
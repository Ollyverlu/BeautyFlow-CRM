import streamlit as st
from banco import conectar, gerar_hash


def mostrar_trocar_senha():

    st.title("🔑 Trocar Senha")

    st.info(
        f"Usuário conectado: {st.session_state['usuario']}"
    )

    senha_atual = st.text_input(
        "Senha atual",
        type="password"
    )

    nova_senha = st.text_input(
        "Nova senha",
        type="password"
    )

    confirmar_nova_senha = st.text_input(
        "Confirmar nova senha",
        type="password"
    )

    if st.button("💾 Alterar Senha"):

        if senha_atual.strip() == "":
            st.error("Digite a senha atual.")

        elif nova_senha.strip() == "":
            st.error("Digite a nova senha.")

        elif len(nova_senha) < 4:
            st.error("A nova senha deve ter pelo menos 4 caracteres.")

        elif nova_senha != confirmar_nova_senha:
            st.error("A nova senha e a confirmação não são iguais.")

        else:
            conn = conectar()
            cursor = conn.cursor()

            senha_atual_hash = gerar_hash(senha_atual)

            cursor.execute("""
                SELECT id
                FROM usuarios
                WHERE usuario = ?
                AND senha = ?
            """, (
                st.session_state["usuario"],
                senha_atual_hash
            ))

            usuario_encontrado = cursor.fetchone()

            if not usuario_encontrado:
                st.error("A senha atual está incorreta.")
                conn.close()

            else:
                nova_senha_hash = gerar_hash(nova_senha)

                cursor.execute("""
                    UPDATE usuarios
                    SET senha = ?
                    WHERE usuario = ?
                """, (
                    nova_senha_hash,
                    st.session_state["usuario"]
                ))

                conn.commit()
                conn.close()

                st.success("Senha alterada com sucesso!")
                st.warning(
                    "Saia do sistema e entre novamente usando a nova senha."
                )
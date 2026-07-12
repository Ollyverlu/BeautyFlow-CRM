
import streamlit as st
import pandas as pd
from banco import conectar


CATEGORIAS_PRODUTOS = [
    "Shampoo",
    "Condicionador",
    "Máscara",
    "Óleo Capilar",
    "Finalizador",
    "Produto para Cílios",
    "Produto para Sobrancelhas",
    "Outro"
]


def mostrar_produtos():

    st.title("🛍️ Gestão de Produtos e Estoque")

    aba1, aba2, aba3 = st.tabs([
        "➕ Cadastrar",
        "✏️ Editar",
        "🗑️ Excluir"
    ])

    # ================= CADASTRAR =================
    with aba1:

        st.subheader("➕ Cadastrar Produto")

        nome_produto = st.text_input("Nome do produto", key="cad_produto_nome")

        categoria_produto = st.selectbox(
            "Categoria do produto",
            CATEGORIAS_PRODUTOS,
            key="cad_produto_categoria"
        )

        preco_produto = st.number_input(
            "Preço do produto (R$)",
            min_value=0.0,
            format="%.2f",
            key="cad_produto_preco"
        )

        quantidade_produto = st.number_input(
            "Quantidade em estoque",
            min_value=0,
            step=1,
            key="cad_produto_quantidade"
        )

        if st.button("💾 Salvar Produto", key="btn_salvar_produto"):

            if nome_produto.strip() == "":
                st.error("Digite o nome do produto.")

            else:
                conn = conectar()
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO produtos
                    (
                        nome,
                        categoria,
                        preco,
                        quantidade
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    nome_produto,
                    categoria_produto,
                    preco_produto,
                    quantidade_produto
                ))

                conn.commit()
                conn.close()

                st.success(f"Produto {nome_produto} cadastrado com sucesso!")

    # ================= EDITAR =================
    with aba2:

        st.subheader("✏️ Editar Produto")

        conn = conectar()

        produtos_df = pd.read_sql_query(
            "SELECT * FROM produtos ORDER BY nome",
            conn
        )

        conn.close()

        if produtos_df.empty:
            st.info("Ainda não existem produtos cadastrados.")

        else:
            produtos_df["opcao"] = (
                produtos_df["id"].astype(str)
                + " - "
                + produtos_df["nome"]
            )

            produto_escolhido = st.selectbox(
                "Escolha o produto",
                produtos_df["opcao"].tolist(),
                key="editar_produto"
            )

            produto_id = int(produto_escolhido.split(" - ")[0])

            linha = produtos_df[
                produtos_df["id"] == produto_id
            ].iloc[0]

            novo_nome = st.text_input(
                "Nome do produto",
                value=str(linha["nome"]),
                key="edit_produto_nome"
            )

            categoria_atual = str(linha["categoria"])

            if categoria_atual in CATEGORIAS_PRODUTOS:
                indice_categoria = CATEGORIAS_PRODUTOS.index(categoria_atual)
            else:
                indice_categoria = 0

            nova_categoria = st.selectbox(
                "Categoria do produto",
                CATEGORIAS_PRODUTOS,
                index=indice_categoria,
                key="edit_produto_categoria"
            )

            novo_preco = st.number_input(
                "Preço do produto (R$)",
                min_value=0.0,
                value=float(linha["preco"]),
                format="%.2f",
                key="edit_produto_preco"
            )

            nova_quantidade = st.number_input(
                "Quantidade em estoque",
                min_value=0,
                value=int(linha["quantidade"]),
                step=1,
                key="edit_produto_quantidade"
            )

            if st.button("💾 Salvar Alterações", key="btn_editar_produto"):

                if novo_nome.strip() == "":
                    st.error("O nome do produto não pode ficar vazio.")

                else:
                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute("""
                        UPDATE produtos
                        SET
                            nome = ?,
                            categoria = ?,
                            preco = ?,
                            quantidade = ?
                        WHERE id = ?
                    """, (
                        novo_nome,
                        nova_categoria,
                        novo_preco,
                        nova_quantidade,
                        produto_id
                    ))

                    conn.commit()
                    conn.close()

                    st.success("Produto atualizado com sucesso!")

    # ================= EXCLUIR =================
    with aba3:

        st.subheader("🗑️ Excluir Produto")

        conn = conectar()

        produtos_excluir_df = pd.read_sql_query(
            "SELECT * FROM produtos ORDER BY nome",
            conn
        )

        conn.close()

        if produtos_excluir_df.empty:
            st.info("Ainda não existem produtos cadastrados.")

        else:
            produtos_excluir_df["opcao"] = (
                produtos_excluir_df["id"].astype(str)
                + " - "
                + produtos_excluir_df["nome"]
            )

            produto_excluir = st.selectbox(
                "Escolha o produto para excluir",
                produtos_excluir_df["opcao"].tolist(),
                key="excluir_produto"
            )

            excluir_id = int(produto_excluir.split(" - ")[0])

            nome_excluir = produtos_excluir_df[
                produtos_excluir_df["id"] == excluir_id
            ].iloc[0]["nome"]

            st.warning(f"Você está prestes a excluir: {nome_excluir}")

            confirmar = st.checkbox(
                "Confirmo que desejo excluir este produto",
                key="confirmar_exclusao_produto"
            )

            if st.button("🗑️ Excluir Produto", key="btn_excluir_produto"):

                if not confirmar:
                    st.error("Marque a confirmação antes de excluir.")

                else:
                    conn = conectar()
                    cursor = conn.cursor()

                    cursor.execute(
                        "DELETE FROM produtos WHERE id = ?",
                        (excluir_id,)
                    )

                    conn.commit()
                    conn.close()

                    st.success(f"Produto {nome_excluir} excluído com sucesso!")
                    st.rerun()

    # ================= LISTA =================
    st.markdown("---")

    st.subheader("📦 Estoque Atual")

    conn = conectar()

    lista_produtos = pd.read_sql_query(
        "SELECT * FROM produtos ORDER BY id DESC",
        conn
    )

    conn.close()

    if lista_produtos.empty:
        st.info("Ainda não existem produtos cadastrados.")
    else:
        st.dataframe(lista_produtos, use_container_width=True)
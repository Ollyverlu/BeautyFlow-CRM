import streamlit as st
import pandas as pd
from banco import conectar


def mostrar_vendas():

    st.title("💰 Gestão de Vendas")

    aba1, aba2, aba3 = st.tabs([
        "➕ Registrar Venda",
        "🧾 Histórico",
        "🗑️ Cancelar Venda"
    ])

    # ================= REGISTRAR VENDA =================
    with aba1:

        st.subheader("➕ Registrar Nova Venda")

        conn = conectar()

        produtos_df = pd.read_sql_query(
            "SELECT * FROM produtos ORDER BY nome",
            conn
        )

        if produtos_df.empty:

            st.warning(
                "Ainda não existem produtos cadastrados. Cadastre um produto primeiro na aba 🛍️ Produtos."
            )

            conn.close()

        else:

            produtos_df["opcao"] = (
                produtos_df["id"].astype(str)
                + " - "
                + produtos_df["nome"]
            )

            produto_escolhido = st.selectbox(
                "Escolha o produto vendido",
                produtos_df["opcao"].tolist(),
                key="venda_produto"
            )

            produto_id = int(
                produto_escolhido.split(" - ")[0]
            )

            produto_linha = produtos_df[
                produtos_df["id"] == produto_id
            ].iloc[0]

            nome_produto = produto_linha["nome"]
            preco_produto = float(produto_linha["preco"])
            estoque_atual = int(produto_linha["quantidade"])

            st.info(f"Produto: {nome_produto}")
            st.info(f"Preço unitário: R$ {preco_produto:.2f}")
            st.info(f"Estoque atual: {estoque_atual}")

            cliente_venda = st.text_input(
                "Nome da cliente",
                key="venda_cliente"
            )

            quantidade_vendida = st.number_input(
                "Quantidade vendida",
                min_value=1,
                max_value=max(1, estoque_atual),
                step=1,
                key="venda_quantidade"
            )

            valor_total = preco_produto * quantidade_vendida

            st.success(
                f"Valor total da venda: R$ {valor_total:.2f}"
            )

            data_venda = st.date_input(
                "Data da venda",
                key="venda_data"
            )

            if st.button(
                "💾 Registrar Venda",
                key="btn_registrar_venda"
            ):

                if estoque_atual <= 0:

                    st.error(
                        "Este produto está sem estoque."
                    )

                elif quantidade_vendida > estoque_atual:

                    st.error(
                        "Quantidade vendida maior que o estoque disponível."
                    )

                else:

                    novo_estoque = estoque_atual - quantidade_vendida
                    cursor = conn.cursor()

                    cursor.execute("""
                        INSERT INTO vendas
                        (
                            produto,
                            quantidade,
                            valor_unitario,
                            valor_total,
                            cliente,
                            data
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        nome_produto,
                        quantidade_vendida,
                        preco_produto,
                        valor_total,
                        cliente_venda,
                        str(data_venda)
                    ))

                    cursor.execute("""
                        UPDATE produtos
                        SET quantidade = ?
                        WHERE id = ?
                    """, (
                        novo_estoque,
                        produto_id
                    ))

                    conn.commit()

                    st.success(
                        "Venda registrada com sucesso!"
                    )

                    st.success(
                        f"Estoque atualizado: {novo_estoque} unidade(s)."
                    )

                    st.markdown("---")
                    st.subheader("🧾 Resumo da Venda")
                    st.write(f"Cliente: {cliente_venda}")
                    st.write(f"Produto: {nome_produto}")
                    st.write(f"Quantidade: {quantidade_vendida}")
                    st.write(f"Valor unitário: R$ {preco_produto:.2f}")
                    st.write(f"Valor total: R$ {valor_total:.2f}")
                    st.write(f"Data: {data_venda}")

            conn.close()

    # ================= HISTÓRICO =================
    with aba2:

        st.subheader("🧾 Histórico de Vendas")

        conn = conectar()

        vendas_df = pd.read_sql_query(
            "SELECT * FROM vendas ORDER BY id DESC",
            conn
        )

        conn.close()

        if vendas_df.empty:

            st.info(
                "Ainda não existem vendas registradas."
            )

        else:

            st.dataframe(
                vendas_df,
                use_container_width=True
            )

            total = vendas_df["valor_total"].sum()
            quantidade = vendas_df["quantidade"].sum()

            col1, col2 = st.columns(2)

            col1.metric(
                "💰 Total vendido",
                f"R$ {total:.2f}"
            )

            col2.metric(
                "📦 Itens vendidos",
                int(quantidade)
            )

    # ================= CANCELAR VENDA =================
    with aba3:

        st.subheader("🗑️ Cancelar Venda")

        st.warning(
            "Ao cancelar uma venda, a quantidade vendida volta automaticamente para o estoque."
        )

        conn = conectar()

        vendas_cancelar_df = pd.read_sql_query(
            "SELECT * FROM vendas ORDER BY id DESC",
            conn
        )

        produtos_df = pd.read_sql_query(
            "SELECT * FROM produtos",
            conn
        )

        if vendas_cancelar_df.empty:

            st.info(
                "Ainda não existem vendas para cancelar."
            )

            conn.close()

        else:

            vendas_cancelar_df["opcao"] = (
                vendas_cancelar_df["id"].astype(str)
                + " - "
                + vendas_cancelar_df["produto"]
                + " - R$ "
                + vendas_cancelar_df["valor_total"].astype(str)
            )

            venda_escolhida = st.selectbox(
                "Escolha a venda para cancelar",
                vendas_cancelar_df["opcao"].tolist(),
                key="cancelar_venda"
            )

            venda_id = int(
                venda_escolhida.split(" - ")[0]
            )

            venda_linha = vendas_cancelar_df[
                vendas_cancelar_df["id"] == venda_id
            ].iloc[0]

            produto_vendido = venda_linha["produto"]
            quantidade_vendida = int(venda_linha["quantidade"])

            st.info(f"Produto vendido: {produto_vendido}")
            st.info(f"Quantidade a devolver ao estoque: {quantidade_vendida}")

            confirmar = st.checkbox(
                "Confirmo que desejo cancelar esta venda",
                key="confirmar_cancelar_venda"
            )

            if st.button(
                "🗑️ Cancelar Venda",
                key="btn_cancelar_venda"
            ):

                if not confirmar:

                    st.error(
                        "Marque a confirmação antes de cancelar."
                    )

                else:

                    cursor = conn.cursor()

                    produto_localizado = produtos_df[
                        produtos_df["nome"] == produto_vendido
                    ]

                    if produto_localizado.empty:

                        st.error(
                            "Produto não encontrado no estoque. Não foi possível devolver a quantidade."
                        )

                    else:

                        produto_id = int(
                            produto_localizado.iloc[0]["id"]
                        )

                        estoque_atual = int(
                            produto_localizado.iloc[0]["quantidade"]
                        )

                        novo_estoque = estoque_atual + quantidade_vendida

                        cursor.execute("""
                            UPDATE produtos
                            SET quantidade = ?
                            WHERE id = ?
                        """, (
                            novo_estoque,
                            produto_id
                        ))

                        cursor.execute(
                            "DELETE FROM vendas WHERE id = ?",
                            (venda_id,)
                        )

                        conn.commit()

                        st.success(
                            "Venda cancelada com sucesso!"
                        )

                        st.success(
                            f"Estoque devolvido. Novo estoque: {novo_estoque} unidade(s)."
                        )

                        conn.close()

                        st.rerun()

            conn.close()
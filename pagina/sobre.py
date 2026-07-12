from pathlib import Path

import streamlit as st


# ==================================================
# CAMINHOS DO PROJETO
# ==================================================
PASTA_PROJETO = Path(__file__).resolve().parent.parent

CAMINHO_LOGO = (
    PASTA_PROJETO
    / "assets"
    / "imagens"
    / "logo_beautyflow.png"
)


# ==================================================
# PÁGINA SOBRE
# ==================================================
def mostrar_sobre():

    st.title("✨ Sobre o BeautyFlow CRM")

    st.caption(
        "Onde a beleza encontra a organização"
    )

    coluna_logo, coluna_texto = st.columns(
        [1, 2]
    )

    with coluna_logo:

        if CAMINHO_LOGO.exists():

            st.image(
                str(CAMINHO_LOGO),
                use_container_width=True
            )

        else:

            st.info(
                "A logo do BeautyFlow CRM "
                "não foi encontrada."
            )

    with coluna_texto:

        st.subheader(
            "💄 BeautyFlow CRM"
        )

        st.write(
            "**Versão 3.0**"
        )

        st.write(
            "Sistema completo de gestão para "
            "profissionais da beleza."
        )

        st.write(
            "Criado para facilitar o controle de "
            "clientes, agenda, produtos, vendas, "
            "financeiro, relatórios e usuários."
        )

    st.markdown("---")

    st.subheader(
        "👩‍💻 Desenvolvido por"
    )

    st.write(
        "### Luciana Oliveira de Albuquerque"
    )

    st.write(
        "**Formada em Tecnologia da Informação**"
    )

    st.write(
        "Desenvolvedora de sistemas com foco em "
        "Python, Streamlit, SQLite, análise de dados "
        "e soluções digitais para necessidades reais."
    )

    st.markdown("---")

    st.subheader(
        "🌸 História do Projeto"
    )

    st.write(
        """
O BeautyFlow CRM foi desenvolvido como um projeto
de evolução profissional, unindo tecnologia,
organização e experiência na área da beleza.

O objetivo do sistema é oferecer uma ferramenta
simples, bonita e funcional para profissionais de
salões de beleza, estética, cílios, cabelo,
micropigmentação e outros serviços.

O projeto também representa uma nova etapa na
trajetória de Luciana Oliveira de Albuquerque,
criadora do LabResíduos e desenvolvedora do
BeautyFlow CRM.
        """
    )

    st.markdown("---")

    st.subheader(
        "🧪 Outros Projetos"
    )

    st.write(
        "### LabResíduos"
    )

    st.write(
        """
Sistema educacional desenvolvido para auxiliar
alunos do IFRJ em cálculos laboratoriais de análises
ambientais, com atenção especial à acessibilidade
para alunos PCD.
        """
    )

    st.markdown("---")

    st.subheader(
        "🛠️ Tecnologias Utilizadas"
    )

    coluna1, coluna2, coluna3 = st.columns(3)

    with coluna1:

        st.write("🐍 **Python**")
        st.write("🌐 **Streamlit**")

    with coluna2:

        st.write("🗄️ **SQLite**")
        st.write("📊 **Pandas**")

    with coluna3:

        st.write("🎨 **CSS**")
        st.write("📑 **OpenPyXL**")

    st.markdown("---")

    st.subheader(
        "🌟 Funcionalidades Principais"
    )

    funcionalidades = [
        "Login com níveis de acesso",
        "Gestão de usuários",
        "Cadastro completo de clientes",
        "Ficha Premium da cliente",
        "Agenda com confirmação pelo WhatsApp",
        "Controle de produtos e estoque",
        "Registro de vendas",
        "Controle financeiro",
        "Caixa do dia",
        "Dashboard executivo",
        "Relatórios com exportação em Excel",
        "Backup do banco de dados",
        "Configurações do estabelecimento"
    ]

    for funcionalidade in funcionalidades:

        st.write(
            f"✅ {funcionalidade}"
        )

    st.markdown("---")

    st.subheader(
        "📌 Informações do Sistema"
    )

    st.write(
        "📅 **Ano de desenvolvimento:** 2026"
    )

    st.write(
        "📦 **Versão:** 3.0"
    )

    st.write(
        "💻 **Plataforma:** Python + Streamlit"
    )

    st.write(
        "🗄️ **Banco de dados:** SQLite"
    )

    st.markdown("---")

    st.success(
        "💜 BeautyFlow CRM — "
        "desenvolvido com dedicação, aprendizado "
        "e paixão por criar soluções úteis."
    )

    st.caption(
        "© 2026 BeautyFlow CRM • "
        "Desenvolvido por Luciana Oliveira de Albuquerque"
    )
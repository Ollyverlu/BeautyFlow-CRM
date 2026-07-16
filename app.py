
from pathlib import Path

import streamlit as st

from banco import criar_tabelas, verificar_login

from pagina.dashboard import mostrar_dashboard
from pagina.servicos import mostrar_servicos
from pagina.produtos import mostrar_produtos
from pagina.vendas import mostrar_vendas
from pagina.financeiro import mostrar_financeiro
from pagina.caixa import mostrar_caixa
from pagina.relatorios import mostrar_relatorios
from pagina.clientes import mostrar_clientes
from pagina.agenda import mostrar_agenda
from pagina.contatos import mostrar_contatos
from pagina.consultar_dados import mostrar_consultar_dados
from pagina.usuarios import mostrar_usuarios
from pagina.backup import mostrar_backup
from pagina.trocar_senha import mostrar_trocar_senha
from pagina.configuracoes import mostrar_configuracoes
from pagina.sobre import mostrar_sobre
from pagina.funcionarios import mostrar_funcionarios
from pagina.comissoes import mostrar_comissoes
from pagina.antes_depois import mostrar_antes_depois


# =========================================================
# CAMINHOS DO PROJETO
# =========================================================
PASTA_PROJETO = Path(__file__).resolve().parent

CAMINHO_CSS = (
    PASTA_PROJETO
    / "assets"
    / "css"
    / "style.css"
)

CAMINHO_LOGO = (
    PASTA_PROJETO
    / "assets"
    / "imagens"
    / "logo_beautyflow.png"
)


# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="BeautyFlow CRM",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CARREGAR O CSS
# =========================================================
def carregar_css():
    if CAMINHO_CSS.exists():
        conteudo_css = CAMINHO_CSS.read_text(
            encoding="utf-8"
        )

        st.markdown(
            f"<style>{conteudo_css}</style>",
            unsafe_allow_html=True
        )


# =========================================================
# INICIAR O SISTEMA
# =========================================================
carregar_css()
criar_tabelas()


# =========================================================
# ESTADO DA SESSÃO
# =========================================================
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""

if "nivel" not in st.session_state:
    st.session_state["nivel"] = ""


# =========================================================
# FUNÇÃO PARA SAIR DO SISTEMA
# =========================================================
def sair_do_sistema():
    st.session_state["logado"] = False
    st.session_state["usuario"] = ""
    st.session_state["nivel"] = ""

    st.rerun()


# =========================================================
# TELA DE LOGIN
# =========================================================
def tela_login():

    st.markdown("<br>", unsafe_allow_html=True)

    coluna_esquerda, coluna_login, coluna_direita = st.columns(
        [1, 1.35, 1]
    )

    with coluna_login:

        if CAMINHO_LOGO.exists():
            st.image(
                str(CAMINHO_LOGO),
                use_container_width=True
            )
        else:
            st.title("✨ BeautyFlow CRM")

            st.caption(
                "Onde a beleza encontra a organização"
            )

            st.warning(
                "A logo ainda não foi encontrada em "
                "assets/imagens/logo_beautyflow.png"
            )

        st.markdown("---")

        st.subheader("🔐 Acesso ao Sistema")

        usuario = st.text_input(
            "Usuário",
            placeholder="Digite seu usuário",
            key="campo_login_usuario"
        )

        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Digite sua senha",
            key="campo_login_senha"
        )

        entrar = st.button(
            "✨ Entrar no BeautyFlow CRM",
            use_container_width=True,
            key="botao_login"
        )

        if entrar:

            if usuario.strip() == "":
                st.error(
                    "Digite o usuário."
                )

            elif senha.strip() == "":
                st.error(
                    "Digite a senha."
                )

            else:
                resultado = verificar_login(
                    usuario.strip(),
                    senha
                )

                if resultado:
                    st.session_state["logado"] = True
                    st.session_state["usuario"] = resultado[0]
                    st.session_state["nivel"] = resultado[1]

                    st.success(
                        "Login realizado com sucesso!"
                    )

                    st.rerun()

                else:
                    st.error(
                        "Usuário ou senha incorretos."
                    )

        st.markdown("---")

        st.caption(
            "BeautyFlow CRM • Desenvolvido por Luciana Ollyver"
        )


# =========================================================
# MENU DO ADMINISTRADOR
# =========================================================
def menu_administrador():

    return st.sidebar.radio(
        "Menu principal",
        [
            "📊 Dashboard",
            "💅 Serviços",
            "👩‍💼 Clientes",
            "📅 Agenda",
            "🛍️ Produtos",
            "💰 Vendas",
            "📸 Antes e Depois",
            "💰 Financeiro",
            "💰 Caixa Diário",
            "📊 Relatórios",
            "📋 Consultar Dados",
            "📱 WhatsApp e Instagram",
            "👥 Gestão de Usuários",
            "📦 Backup",
            "🔑 Trocar Senha",
            "⚙️ Configurações",
            "✨ Sobre o Sistema",
            "👩‍💼 Funcionários",
            "💰 Atendimentos e Comissões"

        ]     
   )


# =========================================================
# MENU DO FUNCIONÁRIO
# =========================================================
def menu_funcionario():

    return st.sidebar.radio(
        "Menu principal",
        [
            "💅 Serviços",
            "👩‍💼 Clientes",
            "📅 Agenda",
            "📱 WhatsApp e Instagram",
            "🔑 Trocar Senha"
        ]
    )


# =========================================================
# ABRIR A PÁGINA ESCOLHIDA
# =========================================================
def abrir_pagina(menu):

    if menu == "📊 Dashboard":
        mostrar_dashboard()

    elif menu == "💅 Serviços":
        mostrar_servicos()

    elif menu == "👩‍💼 Clientes":
        mostrar_clientes()

    elif menu == "📅 Agenda":
        mostrar_agenda()

    elif menu == "🛍️ Produtos":
        mostrar_produtos()

    elif menu == "💰 Vendas":
        mostrar_vendas()

    elif menu == "📸 Antes e Depois":
        mostrar_antes_depois()

    elif menu == "💰 Financeiro":
        mostrar_financeiro()
 
    elif menu == "💰 Caixa Diário": 
       mostrar_caixa()

    elif menu == "📊 Relatórios":
        mostrar_relatorios()

    elif menu == "📋 Consultar Dados":
        mostrar_consultar_dados()

    elif menu == "📱 WhatsApp e Instagram":
        mostrar_contatos()

    elif menu == "👥 Gestão de Usuários":
        mostrar_usuarios()

    elif menu == "📦 Backup":
        mostrar_backup()

    elif menu == "🔑 Trocar Senha":
        mostrar_trocar_senha()

    elif menu == "⚙️ Configurações":
        mostrar_configuracoes()

    elif menu == "✨ Sobre o Sistema":
         mostrar_sobre()   

    elif menu == "👩‍💼 Funcionários":
         mostrar_funcionarios()

    elif menu == "💰 Atendimentos e Comissões":
         mostrar_comissoes()


# =========================================================
# ÁREA PRINCIPAL DO SISTEMA
# =========================================================
def sistema_principal():

    st.sidebar.title(
        "✨ BeautyFlow CRM"
    )

    st.sidebar.caption(
        "Onde a beleza encontra a organização"
    )

    st.sidebar.markdown("---")

    st.sidebar.write(
        f"👤 **Usuário:** "
        f"{st.session_state['usuario']}"
    )

    st.sidebar.write(
        f"🔐 **Nível:** "
        f"{st.session_state['nivel']}"
    )

    if st.sidebar.button(
        "🚪 Sair",
        use_container_width=True,
        key="botao_sair"
    ):
        sair_do_sistema()

    st.sidebar.markdown("---")

    if st.session_state["nivel"] == "Administrador":
        menu = menu_administrador()
    else:
        menu = menu_funcionario()

    abrir_pagina(menu)


# =========================================================
# EXECUÇÃO DO SISTEMA
# =========================================================
if st.session_state["logado"]:
    sistema_principal()
else:
    tela_login()
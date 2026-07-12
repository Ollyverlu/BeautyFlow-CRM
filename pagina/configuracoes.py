from pathlib import Path

import streamlit as st

from banco import conectar


# ==================================================
# CAMINHOS DO PROJETO
# ==================================================
PASTA_PROJETO = Path(__file__).resolve().parent.parent

PASTA_IMAGENS = (
    PASTA_PROJETO
    / "assets"
    / "imagens"
)

PASTA_IMAGENS.mkdir(
    parents=True,
    exist_ok=True
)

CAMINHO_LOGO = (
    PASTA_IMAGENS
    / "logo_beautyflow.png"
)


# ==================================================
# CRIAR TABELA DE CONFIGURAÇÕES
# ==================================================
def criar_tabela_configuracoes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY,
            nome_sistema TEXT,
            slogan TEXT,
            nome_estabelecimento TEXT,
            responsavel TEXT,
            whatsapp TEXT,
            instagram TEXT,
            email TEXT,
            endereco TEXT,
            horario_funcionamento TEXT,
            versao TEXT
        )
        """
    )

    cursor.execute(
        """
        SELECT id
        FROM configuracoes
        WHERE id = 1
        """
    )

    configuracao_existe = cursor.fetchone()

    if not configuracao_existe:

        cursor.execute(
            """
            INSERT INTO configuracoes
            (
                id,
                nome_sistema,
                slogan,
                nome_estabelecimento,
                responsavel,
                whatsapp,
                instagram,
                email,
                endereco,
                horario_funcionamento,
                versao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                "BeautyFlow CRM",
                "Onde a beleza encontra a organização",
                "Luciana Ollyver",
                "Luciana Oliveira de Albuquerque",
                "5521988219493",
                "",
                "",
                "",
                "",
                "3.0"
            )
        )

    conn.commit()
    conn.close()


# ==================================================
# CARREGAR CONFIGURAÇÕES
# ==================================================
def carregar_configuracoes():

    criar_tabela_configuracoes()

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            nome_sistema,
            slogan,
            nome_estabelecimento,
            responsavel,
            whatsapp,
            instagram,
            email,
            endereco,
            horario_funcionamento,
            versao
        FROM configuracoes
        WHERE id = 1
        """
    )

    resultado = cursor.fetchone()

    conn.close()

    if resultado:

        return {
            "nome_sistema": resultado[0] or "",
            "slogan": resultado[1] or "",
            "nome_estabelecimento": resultado[2] or "",
            "responsavel": resultado[3] or "",
            "whatsapp": resultado[4] or "",
            "instagram": resultado[5] or "",
            "email": resultado[6] or "",
            "endereco": resultado[7] or "",
            "horario_funcionamento": resultado[8] or "",
            "versao": resultado[9] or ""
        }

    return {}


# ==================================================
# SALVAR NOVA LOGO
# ==================================================
def salvar_logo(arquivo_logo):

    if arquivo_logo is None:
        return False

    extensao = Path(
        arquivo_logo.name
    ).suffix.lower()

    if extensao not in [
        ".png",
        ".jpg",
        ".jpeg"
    ]:

        st.error(
            "A logo precisa estar no formato "
            "PNG, JPG ou JPEG."
        )

        return False

    dados_imagem = arquivo_logo.getbuffer()

    with open(
        CAMINHO_LOGO,
        "wb"
    ) as arquivo_destino:

        arquivo_destino.write(
            dados_imagem
        )

    return True


# ==================================================
# PÁGINA DE CONFIGURAÇÕES
# ==================================================
def mostrar_configuracoes():

    criar_tabela_configuracoes()

    configuracoes = carregar_configuracoes()

    st.title(
        "⚙️ Configurações do BeautyFlow CRM"
    )

    st.caption(
        "Personalize os dados do estabelecimento "
        "e as informações exibidas no sistema."
    )

    aba1, aba2, aba3 = st.tabs(
        [
            "🏢 Estabelecimento",
            "📱 Contatos",
            "🖼️ Identidade Visual"
        ]
    )

    # ==================================================
    # DADOS DO ESTABELECIMENTO
    # ==================================================
    with aba1:

        st.subheader(
            "🏢 Dados do Estabelecimento"
        )

        nome_sistema = st.text_input(
            "Nome do sistema",
            value=configuracoes.get(
                "nome_sistema",
                "BeautyFlow CRM"
            ),
            key="config_nome_sistema"
        )

        slogan = st.text_input(
            "Slogan",
            value=configuracoes.get(
                "slogan",
                ""
            ),
            key="config_slogan"
        )

        nome_estabelecimento = st.text_input(
            "Nome do estabelecimento",
            value=configuracoes.get(
                "nome_estabelecimento",
                ""
            ),
            key="config_estabelecimento"
        )

        responsavel = st.text_input(
            "Responsável",
            value=configuracoes.get(
                "responsavel",
                ""
            ),
            key="config_responsavel"
        )

        endereco = st.text_area(
            "Endereço",
            value=configuracoes.get(
                "endereco",
                ""
            ),
            key="config_endereco"
        )

        horario_funcionamento = st.text_area(
            "Horário de funcionamento",
            value=configuracoes.get(
                "horario_funcionamento",
                ""
            ),
            placeholder=(
                "Exemplo: Segunda a sábado, "
                "das 9h às 19h"
            ),
            key="config_horario"
        )

        versao = st.text_input(
            "Versão do sistema",
            value=configuracoes.get(
                "versao",
                "3.0"
            ),
            key="config_versao"
        )

    # ==================================================
    # CONTATOS
    # ==================================================
    with aba2:

        st.subheader(
            "📱 Contatos"
        )

        whatsapp = st.text_input(
            "WhatsApp",
            value=configuracoes.get(
                "whatsapp",
                ""
            ),
            placeholder="Exemplo: 5521999999999",
            key="config_whatsapp"
        )

        instagram = st.text_input(
            "Instagram",
            value=configuracoes.get(
                "instagram",
                ""
            ),
            placeholder="@beautyflow",
            key="config_instagram"
        )

        email = st.text_input(
            "E-mail",
            value=configuracoes.get(
                "email",
                ""
            ),
            placeholder="contato@beautyflow.com",
            key="config_email"
        )

    # ==================================================
    # IDENTIDADE VISUAL
    # ==================================================
    with aba3:

        st.subheader(
            "🖼️ Identidade Visual"
        )

        if CAMINHO_LOGO.exists():

            st.write(
                "**Logo atual:**"
            )

            st.image(
                str(CAMINHO_LOGO),
                width=300
            )

        else:

            st.info(
                "Ainda não existe uma logo cadastrada."
            )

        nova_logo = st.file_uploader(
            "Escolha uma nova logo",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            key="config_nova_logo"
        )

        st.info(
            "A nova imagem substituirá a logo atual "
            "do BeautyFlow CRM."
        )

    # ==================================================
    # BOTÃO SALVAR
    # ==================================================
    st.markdown("---")

    if st.button(
        "💾 Salvar Configurações",
        use_container_width=True,
        key="btn_salvar_configuracoes"
    ):

        if nome_sistema.strip() == "":

            st.error(
                "O nome do sistema não pode ficar vazio."
            )

        elif nome_estabelecimento.strip() == "":

            st.error(
                "Digite o nome do estabelecimento."
            )

        else:

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE configuracoes
                SET
                    nome_sistema = ?,
                    slogan = ?,
                    nome_estabelecimento = ?,
                    responsavel = ?,
                    whatsapp = ?,
                    instagram = ?,
                    email = ?,
                    endereco = ?,
                    horario_funcionamento = ?,
                    versao = ?
                WHERE id = 1
                """,
                (
                    nome_sistema.strip(),
                    slogan.strip(),
                    nome_estabelecimento.strip(),
                    responsavel.strip(),
                    whatsapp.strip(),
                    instagram.strip(),
                    email.strip(),
                    endereco.strip(),
                    horario_funcionamento.strip(),
                    versao.strip()
                )
            )

            conn.commit()
            conn.close()

            logo_alterada = salvar_logo(
                nova_logo
            )

            st.success(
                "Configurações salvas com sucesso!"
            )

            if logo_alterada:

                st.success(
                    "Logo atualizada com sucesso!"
                )

            st.rerun()

    
        # ==================================================
    # VISUALIZAÇÃO DOS DADOS SALVOS
    # ==================================================
    st.markdown("---")

    st.subheader("👁️ Visualização")

    # Recarrega os dados depois de salvar
    dados_salvos = carregar_configuracoes()

    st.info(
        "Para acrescentar, retirar ou alterar informações, "
        "use as abas 🏢 Estabelecimento e 📱 Contatos acima "
        "e depois clique em 💾 Salvar Configurações."
    )

    st.write(
        f"### ✨ {dados_salvos.get('nome_sistema', 'BeautyFlow CRM')}"
    )

    slogan_salvo = dados_salvos.get("slogan", "")

    if slogan_salvo:
        st.write(slogan_salvo)

    nome_estabelecimento_salvo = dados_salvos.get(
        "nome_estabelecimento",
        ""
    )

    responsavel_salvo = dados_salvos.get(
        "responsavel",
        ""
    )

    whatsapp_salvo = dados_salvos.get(
        "whatsapp",
        ""
    )

    instagram_salvo = dados_salvos.get(
        "instagram",
        ""
    )

    email_salvo = dados_salvos.get(
        "email",
        ""
    )

    endereco_salvo = dados_salvos.get(
        "endereco",
        ""
    )

    funcionamento_salvo = dados_salvos.get(
        "horario_funcionamento",
        ""
    )

    st.write(
        f"🏢 **Estabelecimento:** "
        f"{nome_estabelecimento_salvo or 'Não informado'}"
    )

    st.write(
        f"👩‍💻 **Responsável:** "
        f"{responsavel_salvo or 'Não informado'}"
    )

    # ==================================================
    # BOTÕES DE CONTATO
    # ==================================================
    col_whatsapp, col_instagram, col_email = st.columns(3)

    with col_whatsapp:

        if whatsapp_salvo:

            numero_whatsapp = "".join(
                caractere
                for caractere in whatsapp_salvo
                if caractere.isdigit()
            )

            st.write(
                f"📱 **WhatsApp:** {whatsapp_salvo}"
            )

            st.link_button(
                "💬 Abrir WhatsApp",
                f"https://wa.me/{numero_whatsapp}",
                use_container_width=True
            )

        else:

            st.write(
                "📱 **WhatsApp:** Não informado"
            )

    with col_instagram:

        if instagram_salvo:

            usuario_instagram = (
                instagram_salvo
                .replace(
                    "https://www.instagram.com/",
                    ""
                )
                .replace(
                    "https://instagram.com/",
                    ""
                )
                .replace("@", "")
                .strip("/")
                .strip()
            )

            st.write(
                f"📸 **Instagram:** @{usuario_instagram}"
            )

            st.link_button(
                "📸 Abrir Instagram",
                (
                    "https://www.instagram.com/"
                    f"{usuario_instagram}"
                ),
                use_container_width=True
            )

        else:

            st.write(
                "📸 **Instagram:** Não informado"
            )

    with col_email:

        if email_salvo:

            st.write(
                f"📧 **E-mail:** {email_salvo}"
            )

            st.link_button(
                "✉️ Enviar E-mail",
                f"mailto:{email_salvo}",
                use_container_width=True
            )

        else:

            st.write(
                "📧 **E-mail:** Não informado"
            )

    st.markdown("---")

    st.write(
        f"📍 **Endereço:** "
        f"{endereco_salvo or 'Não informado'}"
    )

    st.write(
        f"🕒 **Funcionamento:** "
        f"{funcionamento_salvo or 'Não informado'}"
    )

    st.caption(
        f"BeautyFlow CRM • "
        f"Versão {dados_salvos.get('versao', '3.0')} • "
        "Desenvolvido por Luciana Ollyver"
    )
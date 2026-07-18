
from datetime import date, timedelta
from urllib.parse import quote
from pathlib import Path

import streamlit as st

# ==================================================
# CONFIGURAÇÕES
# ==================================================
WHATSAPP_SALAO = "5521988219493"

NOME_ESTABELECIMENTO = "Luciana Ollyver Beauty"

SERVICOS = [
    "Extensão de Cílios",
    "Manutenção de Cílios",
    "Balayagem",
    "Strong",
    "Morena Iluminada",
    "Retoque de Mechas",
    "Corte de Cabelo",
    "Escova Curta",
    "Escova Média",
    "Escova Longa",
    "Hidratação",
    "Reconstrução",
    "Nutrição",
    "Progressiva sem Formol",
    "Botox",
    "Micropigmentação Esfumada",
    "Micropigmentação Fio a Fio",
    "Outro serviço"
]

HORARIOS = [
    "08:00",
    "08:30",
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "12:00",
    "13:00",
    "13:30",
    "14:00",
    "14:30",
    "15:00",
    "15:30",
    "16:00",
    "16:30",
    "17:00",
    "17:30",
    "18:00"
]


# ==================================================
# CONFIGURAÇÃO DA PÁGINA
# ==================================================
st.set_page_config(
    page_title="Agendamento | Luciana Ollyver Beauty",
    page_icon="🌸",
    layout="centered"
)


# ==================================================
# ESTILO
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background:
            linear-gradient(
                145deg,
                #fff7fb 0%,
                #fce8f2 50%,
                #f8dce9 100%
            );
    }

    .block-container {
        max-width: 760px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        text-align: center;
        color: #6d2947 !important;
    }

    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(150, 72, 107, 0.18);
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(94, 46, 67, 0.10);
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
    }

    .stButton > button,
    .stLinkButton > a {
        min-height: 50px;
        border-radius: 14px !important;
        font-weight: 700 !important;
    }

    .rodape {
        text-align: center;
        color: #70465a;
        font-size: 14px;
        margin-top: 28px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# FUNÇÃO DO WHATSAPP
# ==================================================
def criar_link_whatsapp(
    nome_cliente,
    telefone_cliente,
    servico,
    data_agendamento,
    horario,
    observacao
):
    data_formatada = data_agendamento.strftime(
        "%d/%m/%Y"
    )

    mensagem = (
        f"Olá, Luciana! 🌸\n\n"
        f"Gostaria de solicitar um agendamento.\n\n"
        f"👩 Cliente: {nome_cliente}\n"
        f"📱 Telefone: {telefone_cliente}\n"
        f"💇 Serviço: {servico}\n"
        f"📅 Data desejada: {data_formatada}\n"
        f"🕒 Horário desejado: {horario}\n"
    )

    if observacao.strip():
        mensagem += (
            f"📝 Observação: {observacao.strip()}\n"
        )

    mensagem += (
        "\nAguardo a confirmação do horário. "
        "Obrigada! 💜"
    )

    return (
        f"https://wa.me/{WHATSAPP_SALAO}"
        f"?text={quote(mensagem)}"
    )
# ==================================================
# BANNER
# ==================================================

CAMINHO_BANNER = (
    Path(__file__).resolve().parent
    / "assets"
    / "imagens"
    / "clientes"
    / "banner_principal.png"
)

if CAMINHO_BANNER.exists():

    st.image(
        str(CAMINHO_BANNER),
        use_container_width=True
    )

else:

    st.error(
        f"Banner não encontrado em:\n{CAMINHO_BANNER}"
    )

# ==================================================
# CABEÇALHO
# ==================================================

st.title("🌸 Luciana Ollyver Beauty")

st.markdown(
    """
### 🌸 Bem-vinda!

Sou **Luciana Oliveira de Albuquerque**, especialista em beleza, apaixonada por transformar a autoestima das minhas clientes através de técnicas modernas e atendimento personalizado.

Será um prazer cuidar de você!

✨ Agende seu horário e venha viver uma experiência de beleza feita com carinho.
"""
)

# ==================================================
# NOSSOS SERVIÇOS
# ==================================================

st.markdown("---")

st.markdown("## 💇 Nossos Serviços")

col1, col2 = st.columns(2)

with col1:

    st.info("""
👁️ **Extensão de Cílios**

Realce seu olhar com técnicas modernas e acabamento natural.
""")

    st.info("""
💇 **Mechas e Balayagem**

Ilumine seus cabelos com técnicas profissionais.
""")

    st.info("""
💆 **Tratamentos Capilares**

Hidratação • Nutrição • Reconstrução
""")

with col2:

    st.info("""
💄 **Maquiagem Profissional**

Para festas, eventos e ocasiões especiais.
""")

    st.info("""
💋 **Micropigmentação**

Sobrancelhas com efeito natural.
""")

    st.info("""
✨ **Progressiva e Botox**

Cabelos alinhados, brilhantes e saudáveis.
""")

# ==================================================
# CABEÇALHO
# =================================================
   
st.title("🌸 Luciana Ollyver Beauty")

st.markdown(
    """
    <h3>Agendamento Online</h3>
    <p style="
        text-align:center;
        color:#70465a;
        font-size:17px;
    ">
        Escolha o serviço, a data e o horário desejado.
        O pedido será enviado diretamente para o nosso WhatsApp.
    </p>
    """,
    unsafe_allow_html=True
)

st.info(
    "O envio deste formulário é uma solicitação. "
    "O horário será confirmado pelo WhatsApp."
)


# ==================================================
# GALERIA AUTOMÁTICA
# ==================================================

st.markdown("---")
st.markdown("## 📸 Trabalhos Realizados")

PASTA_GALERIA = (
    Path(__file__).resolve().parent
    / "assets"
    / "imagens"
    / "antes_depois"
)

EXTENSOES_PERMITIDAS = {
    ".png",
    ".jpg",
    ".jpeg"
}

fotos_galeria = []

if PASTA_GALERIA.exists():

    fotos_galeria = sorted(
        [
            arquivo
            for arquivo in PASTA_GALERIA.iterdir()
            if (
                arquivo.is_file()
                and arquivo.suffix.lower()
                in EXTENSOES_PERMITIDAS
            )
        ],
        reverse=True
    )

if not fotos_galeria:

    st.info(
        "A galeria será exibida quando houver "
        "fotos cadastradas no Antes e Depois."
    )

else:

    # Mostra no máximo 12 imagens
    fotos_exibir = fotos_galeria[:12]

    for inicio in range(
        0,
        len(fotos_exibir),
        3
    ):

        colunas = st.columns(3)

        grupo = fotos_exibir[
            inicio:inicio + 3
        ]

        for coluna, caminho_foto in zip(
            colunas,
            grupo
        ):

            with coluna:

                nome_legenda = (
                    caminho_foto.stem
                    .replace("_antes_", " • Antes • ")
                    .replace("_depois_", " • Depois • ")
                    .replace("_", " ")
                    .title()
                )

                st.image(
                    str(caminho_foto),
                    caption=nome_legenda,
                    use_container_width=True
                )

# ==================================================
# FORMULÁRIO
# ==================================================
with st.form(
    "formulario_agendamento",
    clear_on_submit=False
):

    nome_cliente = st.text_input(
        "Seu nome completo *",
        placeholder="Digite seu nome"
    )

    telefone_cliente = st.text_input(
        "Seu WhatsApp *",
        placeholder="Exemplo: (21) 99999-9999"
    )

    servico = st.selectbox(
        "Serviço desejado *",
        SERVICOS
    )

    outro_servico = ""

    if servico == "Outro serviço":
        outro_servico = st.text_input(
            "Qual serviço você deseja?",
            placeholder="Digite o serviço"
        )

    coluna_data, coluna_horario = st.columns(2)

    with coluna_data:

        data_agendamento = st.date_input(
            "Data desejada *",
            value=date.today() + timedelta(days=1),
            min_value=date.today(),
            max_value=date.today() + timedelta(days=180),
            format="DD/MM/YYYY"
        )

    with coluna_horario:

        horario = st.selectbox(
            "Horário desejado *",
            HORARIOS
        )

    observacao = st.text_area(
        "Observação",
        placeholder=(
            "Informe alguma preferência ou dúvida."
        )
    )

    preparar_mensagem = st.form_submit_button(
        "📱 Preparar agendamento pelo WhatsApp",
        use_container_width=True
    )


# ==================================================
# RESULTADO
# ==================================================
if preparar_mensagem:

    servico_final = (
        outro_servico.strip()
        if servico == "Outro serviço"
        else servico
    )

    if nome_cliente.strip() == "":

        st.error(
            "Digite seu nome para continuar."
        )

    elif telefone_cliente.strip() == "":

        st.error(
            "Digite seu WhatsApp para continuar."
        )

    elif servico_final == "":

        st.error(
            "Digite o serviço desejado."
        )

    else:

        link_whatsapp = criar_link_whatsapp(
            nome_cliente=nome_cliente.strip(),
            telefone_cliente=telefone_cliente.strip(),
            servico=servico_final,
            data_agendamento=data_agendamento,
            horario=horario,
            observacao=observacao
        )

        st.success(
            "Solicitação preparada! Clique no botão "
            "abaixo para enviar pelo WhatsApp."
        )

        st.link_button(
            "💬 Enviar solicitação para Luciana",
            link_whatsapp,
            use_container_width=True
        )

        st.warning(
            "O agendamento só estará confirmado "
            "depois da resposta do salão."
        )


# ==================================================
# RODAPÉ
# ==================================================
st.markdown(
    f"""
    <div class="rodape">
        <strong>{NOME_ESTABELECIMENTO}</strong><br>
        Atendimento mediante confirmação pelo WhatsApp.<br><br>
        Tecnologia BeautyFlow CRM
    </div>
    """,
    unsafe_allow_html=True
)
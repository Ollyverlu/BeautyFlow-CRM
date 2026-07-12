# ✨ BeautyFlow CRM

> Onde a beleza encontra a organização.

Sistema completo de gestão para profissionais da beleza, desenvolvido em Python com Streamlit e SQLite.

O BeautyFlow CRM foi criado para facilitar o controle de clientes, agenda, produtos, vendas, estoque, financeiro, relatórios e usuários em salões de beleza, espaços de estética, lash designers, cabeleireiros e outros profissionais do setor.

---

## 👩‍💻 Desenvolvido por

**Luciana Oliveira de Albuquerque**

Formada em Tecnologia da Informação, com conhecimentos em Python, Streamlit, SQLite, Pandas, Power BI, SQL, AWS e desenvolvimento de soluções digitais.

---

## 🌸 Funcionalidades

- Login com níveis de acesso
- Gestão de usuários
- Troca de senha
- Cadastro completo de clientes
- Foto da cliente
- WhatsApp e Instagram
- Ficha Premium da cliente
- Pesquisa e edição de clientes
- Agenda de atendimentos
- Confirmação de agendamento pelo WhatsApp
- Bloqueio de horários duplicados
- Cadastro de serviços
- Cadastro de produtos
- Controle de estoque
- Alerta de estoque baixo
- Registro de vendas
- Baixa automática no estoque
- Controle financeiro
- Entradas e saídas
- Caixa do dia
- Dashboard executivo
- Aniversariantes do dia
- Próximo atendimento
- Dicas do dia
- Relatórios executivos
- Rankings de clientes, produtos e serviços
- Exportação para Excel
- Exportação para PDF
- Backup do banco de dados
- Configurações do estabelecimento
- Personalização da logo
- Tela “Sobre o Sistema”

---

## 🛠️ Tecnologias utilizadas

- Python
- Streamlit
- SQLite
- Pandas
- OpenPyXL
- ReportLab
- Pillow
- CSS

---

## 📁 Estrutura do projeto

```text
CRM_Beleza
│
├── app.py
├── banco.py
├── config.py
├── requirements.txt
├── README.md
│
├── assets
│   ├── css
│   │   └── style.css
│   ├── imagens
│   │   └── logo_beautyflow.png
│   └── icones
│
├── pagina
│   ├── agenda.py
│   ├── backup.py
│   ├── caixa.py
│   ├── clientes.py
│   ├── configuracoes.py
│   ├── consultar_dados.py
│   ├── contatos.py
│   ├── dashboard.py
│   ├── financeiro.py
│   ├── produtos.py
│   ├── relatorios.py
│   ├── servicos.py
│   ├── sobre.py
│   ├── trocar_senha.py
│   ├── usuarios.py
│   └── vendas.py
│
└── utils
    ├── cards.py
    ├── componentes.py
    ├── estilos.py
    └── graficos.py
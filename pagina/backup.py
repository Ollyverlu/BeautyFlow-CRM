import streamlit as st
import os
import shutil
from datetime import datetime


CAMINHO_BANCO = "crm_beleza.db"
PASTA_BACKUP = "backups"


def mostrar_backup():

    st.title("📦 Backup do Sistema")

    st.info(
        "Nesta área você pode criar e baixar uma cópia de segurança "
        "do banco de dados do CRM Beleza."
    )

    if not os.path.exists(PASTA_BACKUP):
        os.makedirs(PASTA_BACKUP)

    if not os.path.exists(CAMINHO_BANCO):

        st.error(
            "O banco de dados crm_beleza.db não foi encontrado."
        )

        return

    st.subheader("💾 Criar Backup")

    if st.button("Criar Backup Agora"):

        data_hora = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        nome_backup = (
            f"crm_beleza_backup_{data_hora}.db"
        )

        caminho_backup = os.path.join(
            PASTA_BACKUP,
            nome_backup
        )

        shutil.copy2(
            CAMINHO_BANCO,
            caminho_backup
        )

        st.success(
            "Backup criado com sucesso!"
        )

        with open(caminho_backup, "rb") as arquivo:

            st.download_button(
                label="📥 Baixar Backup",
                data=arquivo,
                file_name=nome_backup,
                mime="application/octet-stream"
            )

    st.markdown("---")

    st.subheader("📋 Backups Criados")

    arquivos_backup = []

    if os.path.exists(PASTA_BACKUP):

        arquivos_backup = [
            arquivo
            for arquivo in os.listdir(PASTA_BACKUP)
            if arquivo.endswith(".db")
        ]

    arquivos_backup.sort(reverse=True)

    if not arquivos_backup:

        st.info(
            "Ainda não existem backups criados."
        )

    else:

        backup_escolhido = st.selectbox(
            "Escolha um backup para baixar",
            arquivos_backup
        )

        caminho_escolhido = os.path.join(
            PASTA_BACKUP,
            backup_escolhido
        )

        with open(caminho_escolhido, "rb") as arquivo:

            st.download_button(
                label="📥 Baixar Backup Selecionado",
                data=arquivo,
                file_name=backup_escolhido,
                mime="application/octet-stream"
            )
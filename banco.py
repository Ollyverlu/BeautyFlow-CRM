import sqlite3
import hashlib


def conectar():
    return sqlite3.connect(
        "crm_beleza.db",
        check_same_thread=False
    )


# ================= PROTEÇÃO DA SENHA =================
def gerar_hash(senha):
    return hashlib.sha256(
        senha.encode("utf-8")
    ).hexdigest()


def senha_esta_protegida(senha):
    if senha is None or len(senha) != 64:
        return False

    try:
        int(senha, 16)
        return True
    except ValueError:
        return False


# ================= CRIAÇÃO DAS TABELAS =================
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        telefone TEXT,
        servico TEXT,
        observacao TEXT
    )
    """)

    # ==================================================
    # NOVOS CAMPOS DA FICHA DA CLIENTE
    # ==================================================
    novos_campos = [
        ("email", "TEXT"),
        ("instagram", "TEXT"),
        ("nascimento", "TEXT"),
        ("endereco", "TEXT"),
        ("servico_favorito", "TEXT"),
        ("total_gasto", "REAL DEFAULT 0"),
        ("foto", "TEXT")
    ]

    cursor.execute("PRAGMA table_info(clientes)")

    colunas_existentes = [
        coluna[1]
        for coluna in cursor.fetchall()
    ]

    for campo, tipo in novos_campos:
        if campo not in colunas_existentes:
            cursor.execute(
                f"ALTER TABLE clientes ADD COLUMN {campo} {tipo}"
            )




    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        data TEXT,
        horario TEXT,
        servico TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        categoria TEXT,
        preco REAL,
        quantidade INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        descricao TEXT,
        categoria TEXT,
        valor REAL,
        forma_pagamento TEXT,
        data TEXT,
        observacao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto TEXT,
        quantidade INTEGER,
        valor_unitario REAL,
        valor_total REAL,
        cliente TEXT,
        data TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT,
        nivel TEXT
    )
    """)

    # Cria os usuários padrão somente se ainda não existirem.
    cursor.execute("""
        INSERT OR IGNORE INTO usuarios
        (usuario, senha, nivel)
        VALUES (?, ?, ?)
    """, (
        "admin",
        gerar_hash("1234"),
        "Administrador"
    ))

    cursor.execute("""
        INSERT OR IGNORE INTO usuarios
        (usuario, senha, nivel)
        VALUES (?, ?, ?)
    """, (
        "funcionario",
        gerar_hash("1234"),
        "Funcionário"
    ))

    # Converte senhas antigas, salvas como texto, apenas uma vez.
    cursor.execute("""
        SELECT id, senha
        FROM usuarios
    """)

    usuarios = cursor.fetchall()

    for usuario_id, senha_salva in usuarios:
        if senha_salva and not senha_esta_protegida(senha_salva):
            cursor.execute("""
                UPDATE usuarios
                SET senha = ?
                WHERE id = ?
            """, (
                gerar_hash(senha_salva),
                usuario_id
            ))

    conn.commit()
    conn.close()


# ================= VERIFICAR LOGIN =================
def verificar_login(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT usuario, nivel
        FROM usuarios
        WHERE usuario = ?
        AND senha = ?
    """, (
        usuario.strip(),
        gerar_hash(senha)
    ))

    resultado = cursor.fetchone()

    conn.close()

    return resultado

from banco import conectar


def registrar_entrada_financeiro(
    descricao,
    valor,
    forma_pagamento,
    data,
    observacao=""
):
    """
    Registra automaticamente uma entrada
    no Financeiro.
    """

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO financeiro
        (
            tipo,
            descricao,
            categoria,
            valor,
            forma_pagamento,
            data,
            observacao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Entrada",
            descricao,
            "Serviço Realizado",
            float(valor),
            forma_pagamento,
            str(data),
            observacao
        )
    )

    conn.commit()

    financeiro_id = cursor.lastrowid

    conn.close()

    return financeiro_id
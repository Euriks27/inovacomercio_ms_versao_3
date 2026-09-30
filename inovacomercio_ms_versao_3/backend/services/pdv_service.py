# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from datetime import date

from backend.database import db
from backend.models.product import Product
from backend.models.stock_movement import StockMovement
from backend.models.transaction import Transaction
from backend.schemas.pdv import (
    PdvItemProcessado,
    PdvVendaRequest,
    PdvVendaResponse,
)


def processar_venda(payload: PdvVendaRequest) -> PdvVendaResponse:
    """Processa uma venda de PDV: valida estoque, baixa, gera transação."""

    itens_processados: list[PdvItemProcessado] = []
    total = 0.0
    baixas = 0

    # Primeira passagem: valida tudo antes de baixar
    for item in payload.itens:
        produto = Product.query.get(int(item.sku)) if item.sku.isdigit() else None
        if produto is None:
            raise ValueError(f"Produto não encontrado: {item.sku}")

        if produto.estoque_atual < item.quantidade:
            raise ValueError(
                f"Estoque insuficiente para {produto.produto}: "
                f"disponível {produto.estoque_atual}, pedido {item.quantidade}"
            )

    # Segunda passagem: processa
    for item in payload.itens:
        produto = Product.query.get(int(item.sku))

        subtotal = produto.preco_sugerido * item.quantidade

        produto.estoque_atual -= item.quantidade

        db.session.add(
            StockMovement(
                product_id=produto.id,
                tipo="SAIDA",
                quantidade=item.quantidade,
                motivo="VENDA",
            )
        )

        itens_processados.append(
            PdvItemProcessado(
                sku=str(produto.id),
                nome=produto.produto,
                quantidade=item.quantidade,
                preco_unitario=produto.preco_sugerido,
                subtotal=subtotal,
            )
        )

        total += subtotal
        baixas += 1

    # Transação financeira
    transacao = Transaction(
        data=date.today(),
        tipo="receita",
        descricao=f"Venda PDV {payload.pdv_id}",
        valor=total,
        origem="PDV",
    )
    db.session.add(transacao)
    db.session.commit()

    return PdvVendaResponse(
        venda_id=f"VD-{uuid.uuid4().hex[:8].upper()}",
        total=round(total, 2),
        forma_pagamento=payload.forma_pagamento,
        itens=itens_processados,
        transacao_id=transacao.id,
        baixas_estoque=baixas,
    )
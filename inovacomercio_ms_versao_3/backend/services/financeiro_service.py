# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import date

from backend.database import db
from backend.models.transaction import Transaction
from backend.schemas.financeiro import (
    DreResumo,
    FinanceiroResumo,
    TransacaoCreate,
    TransacaoOut,
)


def listar_transacoes(limit: int = 200) -> FinanceiroResumo:
    rows = (
        Transaction.query
        .order_by(Transaction.data.desc(), Transaction.id.desc())
        .limit(limit)
        .all()
    )

    transacoes = [
        TransacaoOut(
            id=t.id,
            data=t.data.isoformat() if t.data else "",
            tipo=t.tipo,
            descricao=t.descricao,
            valor=t.valor,
            origem=t.origem or "MANUAL",
        )
        for t in rows
    ]

    todas = Transaction.query.all()
    receitas = sum(t.valor for t in todas if t.tipo == "receita")
    despesas = sum(t.valor for t in todas if t.tipo == "despesa")
    lucro = receitas - despesas
    margem = (lucro / receitas) if receitas > 0 else 0.0

    return FinanceiroResumo(
        transacoes=transacoes,
        dre=DreResumo(
            receitas=round(receitas, 2),
            despesas=round(despesas, 2),
            lucro=round(lucro, 2),
            margem_liquida=round(margem, 4),
        ),
    )


def criar_transacao(payload: TransacaoCreate) -> TransacaoOut:
    t = Transaction(
        data=date.today(),
        tipo=payload.tipo,
        descricao=payload.descricao,
        valor=payload.valor,
        origem="MANUAL",
    )
    db.session.add(t)
    db.session.commit()

    return TransacaoOut(
        id=t.id,
        data=t.data.isoformat(),
        tipo=t.tipo,
        descricao=t.descricao,
        valor=t.valor,
        origem=t.origem,
    )
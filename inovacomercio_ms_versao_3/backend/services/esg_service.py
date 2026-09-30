# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import date

from backend.database import db
from backend.models.esg_log import ESG_FATORES, EsgLog
from backend.models.transaction import Transaction
from backend.schemas.esg import (
    EsgHistoricoResponse,
    LogisticaReversaOut,
    LogisticaReversaRequest,
)


def registrar_logistica_reversa(
    payload: LogisticaReversaRequest,
) -> LogisticaReversaOut:
    fator = ESG_FATORES.get(payload.material, 0.03)
    credito = round(payload.quantidade * fator, 2)

    log = EsgLog(
        material=payload.material.upper(),
        quantidade=payload.quantidade,
        credito_gerado=credito,
    )
    db.session.add(log)

    # Gera receita simbólica de crédito verde
    db.session.add(
        Transaction(
            data=date.today(),
            tipo="receita",
            descricao=f"Crédito Verde — {payload.material.upper()}",
            valor=credito,
            origem="ESG",
        )
    )

    db.session.commit()

    return LogisticaReversaOut(
        id=log.id,
        material=log.material,
        quantidade=log.quantidade,
        credito_gerado=log.credito_gerado,
        data=log.criado_em.date().isoformat(),
    )


def historico_logistica() -> EsgHistoricoResponse:
    logs = EsgLog.query.order_by(EsgLog.criado_em.desc()).limit(50).all()

    registros = [
        LogisticaReversaOut(
            id=l.id,
            material=l.material,
            quantidade=l.quantidade,
            credito_gerado=l.credito_gerado,
            data=l.criado_em.date().isoformat(),
        )
        for l in logs
    ]

    total = sum(l.credito_gerado for l in logs)

    return EsgHistoricoResponse(
        logs=registros,
        credito_total=round(total, 2),
    )
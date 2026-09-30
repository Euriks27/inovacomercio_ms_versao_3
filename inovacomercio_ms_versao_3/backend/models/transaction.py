# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime

from backend.app.database import db


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # ENTRADA | SAIDA | AJUSTE
    quantidade = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(120), nullable=False, default="VENDA")
    tenant_id = db.Column(db.String(50), nullable=False, default="demo_ms")
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "tipo": self.tipo,
            "quantidade": self.quantidade,
            "motivo": self.motivo,
            "criado_em": self.criado_em.isoformat(),
        }
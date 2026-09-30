# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime

from backend.app.database import db

ESG_FATORES = {
    "vidro": 0.10,
    "pet": 0.05,
    "papelao": 0.03,
    "oleo": 0.20,
    "eletronicos": 0.15,
}


class EsgLog(db.Model):
    __tablename__ = "esg_logs"

    id = db.Column(db.Integer, primary_key=True)
    material = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    credito_gerado = db.Column(db.Float, nullable=False)
    tenant_id = db.Column(db.String(50), nullable=False, default="demo_ms")
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "material": self.material,
            "quantidade": self.quantidade,
            "credito_gerado": self.credito_gerado,
            "data": self.criado_em.date().isoformat(),
        }
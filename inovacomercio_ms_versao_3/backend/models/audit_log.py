# -*- coding: utf-8 -*-
from __future__ import annotations

from backend.app.database import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    usuario = db.Column(db.String(80), nullable=False)

    evento = db.Column(db.String(100), nullable=False)

    modulo = db.Column(db.String(80), nullable=False)

    ts = db.Column(db.Integer, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "usuario": self.usuario,
            "evento": self.evento,
            "modulo": self.modulo,
            "ts": self.ts,
        }
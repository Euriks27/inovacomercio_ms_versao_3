# -*- coding: utf-8 -*-
from __future__ import annotations

from backend.app.database import db  # ✅ mesmo db dos outros


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    produto = db.Column(db.String(120), nullable=False, index=True)
    categoria = db.Column(db.String(60), nullable=False, default="Mercearia")
    custo = db.Column(db.Float, nullable=False)
    markup = db.Column(db.Float, nullable=False)
    preco_sugerido = db.Column(db.Float, nullable=False)
    margem = db.Column(db.Float, nullable=False)
    estoque_atual = db.Column(db.Integer, nullable=False, default=0)
    estoque_minimo = db.Column(db.Integer, nullable=False, default=5)

    @property
    def sku(self) -> str:
        return f"SKU-{self.id:04d}"

    @property
    def ponto_pedido(self) -> int:
        return self.estoque_minimo + 5

    @property
    def abaixo_minimo(self) -> bool:
        return self.estoque_atual < self.estoque_minimo

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sku": self.sku,
            "produto": self.produto,
            "categoria": self.categoria,
            "custo": self.custo,
            "markup": self.markup,
            "preco_sugerido": self.preco_sugerido,
            "margem": self.margem,
            "estoque_atual": self.estoque_atual,
            "estoque_minimo": self.estoque_minimo,
        }
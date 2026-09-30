# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class PdvItem(BaseModel):
    sku: str
    quantidade: int = Field(gt=0)


class PdvVendaRequest(BaseModel):
    itens: List[PdvItem] = Field(min_length=1)
    forma_pagamento: str = Field(default="dinheiro")
    pdv_id: str = Field(default="PDV-01")


class PdvItemProcessado(BaseModel):
    sku: str
    nome: str
    quantidade: int
    preco_unitario: float
    subtotal: float


class PdvVendaResponse(BaseModel):
    venda_id: str
    total: float
    forma_pagamento: str
    itens: List[PdvItemProcessado]
    transacao_id: int
    baixas_estoque: int
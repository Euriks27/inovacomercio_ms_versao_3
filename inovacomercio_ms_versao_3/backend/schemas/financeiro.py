# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TransacaoCreate(BaseModel):
    tipo: str = Field(pattern="^(receita|despesa)$")
    descricao: str = Field(min_length=2, max_length=255)
    valor: float = Field(gt=0)


class TransacaoOut(BaseModel):
    id: int
    data: str
    tipo: str
    descricao: str
    valor: float
    origem: str


class DreResumo(BaseModel):
    receitas: float
    despesas: float
    lucro: float
    margem_liquida: float


class FinanceiroResumo(BaseModel):
    transacoes: List[TransacaoOut]
    dre: DreResumo
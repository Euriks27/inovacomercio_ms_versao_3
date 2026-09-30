# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ProdutoCreate(BaseModel):
    produto: str = Field(min_length=2, max_length=120)
    custo: float = Field(ge=0)
    markup: float = Field(gt=1.0)
    categoria: str = Field(default="Mercearia")
    estoque_atual: int = Field(default=0, ge=0)
    estoque_minimo: int = Field(default=5, ge=0)


class ProdutoUpdate(BaseModel):
    produto: Optional[str] = Field(default=None, min_length=2, max_length=120)
    custo: Optional[float] = Field(default=None, ge=0)
    markup: Optional[float] = Field(default=None, gt=1.0)
    categoria: Optional[str] = None
    estoque_atual: Optional[int] = Field(default=None, ge=0)
    estoque_minimo: Optional[int] = Field(default=None, ge=0)


class ProdutoEstoque(BaseModel):
    id: int
    sku: str
    produto: str
    categoria: str
    custo: float
    preco_sugerido: float
    margem: float
    estoque_atual: int
    estoque_minimo: int
    ponto_pedido: int
    cobertura_dias: int
    abaixo_minimo: bool


class MovimentacaoRequest(BaseModel):
    product_id: int
    tipo: str = Field(pattern="^(ENTRADA|SAIDA|AJUSTE)$")
    quantidade: int = Field(gt=0)
    motivo: str = Field(default="AJUSTE_MANUAL")
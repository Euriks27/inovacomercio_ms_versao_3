# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class LogisticaReversaRequest(BaseModel):
    material: str = Field(pattern="^(vidro|pet|papelao|oleo|eletronicos)$")
    quantidade: float = Field(gt=0)


class LogisticaReversaOut(BaseModel):
    id: int
    material: str
    quantidade: float
    credito_gerado: float
    data: str


class EsgHistoricoResponse(BaseModel):
    logs: List[LogisticaReversaOut]
    credito_total: float
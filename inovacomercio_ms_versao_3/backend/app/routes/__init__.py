# -*- coding: utf-8 -*-
from __future__ import annotations

from backend.app.routes.esg_routes import bp as esg_bp
from backend.app.routes.estoque_routes import bp as estoque_bp
from backend.app.routes.financeiro_routes import bp as financeiro_bp
from backend.app.routes.pdv_routes import bp as pdv_bp

__all__ = ["esg_bp", "estoque_bp", "financeiro_bp", "pdv_bp"]

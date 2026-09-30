# -*- coding: utf-8 -*-
"""
Instância única do SQLAlchemy para todo o backend.

Uso:
    from backend.database import db
    db.init_app(app)   # chamado uma vez no app.py
"""
from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
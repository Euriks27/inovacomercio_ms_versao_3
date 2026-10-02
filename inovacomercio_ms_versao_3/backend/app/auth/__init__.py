# -*- coding: utf-8 -*-
"""Módulo de autenticação com suporte a hashing de senhas, validação e JWT."""
from __future__ import annotations

from backend.app.auth.password_service import PasswordService
from backend.app.auth.schemas import LoginRequest, LoginResponse
from backend.app.auth.service import AuthService

__all__ = ["AuthService", "PasswordService", "LoginRequest", "LoginResponse"]

# -*- coding: utf-8 -*-
"""Schemas Pydantic para autenticação e autorização."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    Requisição de login com validação de entrada.
    
    ✅ Email validado via EmailStr (RFC 5322)
    ✅ Senha com comprimento mínimo e máximo
    """
    email: EmailStr = Field(
        ...,
        description="Email do usuário",
        examples=["gestor@inovacomercio.ms"]
    )
    senha: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Senha do usuário (6-128 caracteres)"
    )

    class Config:
        """Configuração do modelo."""
        json_schema_extra = {
            "example": {
                "email": "gestor@inovacomercio.ms",
                "senha": "minha_senha_segura"
            }
        }


class UserResponse(BaseModel):
    """Dados do usuário retornados após login bem-sucedido."""
    id: int = Field(..., description="ID único do usuário")
    nome: str = Field(..., description="Nome completo")
    email: str = Field(..., description="Email")
    role: str = Field(..., description="Papel (admin, gestor, operador)")
    tenant_id: str = Field(..., description="ID do tenant")


class LoginResponse(BaseModel):
    """
    Resposta de login com JWT token e dados do usuário.
    
    ✅ Token seguro com expiração
    ✅ Dados do usuário inclusos
    """
    access_token: str = Field(..., description="JWT token para autorização")
    token_type: str = Field(
        default="Bearer",
        description="Tipo de token (sempre Bearer)"
    )
    expires_in: int = Field(
        ...,
        description="Expiração do token em segundos"
    )
    usuario: UserResponse = Field(..., description="Dados do usuário autenticado")

    class Config:
        """Configuração do modelo."""
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "token_type": "Bearer",
                "expires_in": 3600,
                "usuario": {
                    "id": 1,
                    "nome": "Gestor InovaComércio",
                    "email": "gestor@inovacomercio.ms",
                    "role": "admin",
                    "tenant_id": "demo_ms"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Resposta de erro padronizada."""
    error: str = Field(..., description="Mensagem de erro")
    status_code: int = Field(..., description="Código HTTP")
    details: dict | None = Field(
        default=None,
        description="Detalhes adicionais do erro"
    )

    class Config:
        """Configuração do modelo."""
        json_schema_extra = {
            "example": {
                "error": "Credenciais inválidas",
                "status_code": 401,
                "details": {"email": "Email ou senha incorretos"}
            }
        }

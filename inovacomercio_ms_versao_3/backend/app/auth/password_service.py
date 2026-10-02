# -*- coding: utf-8 -*-
"""Serviço para hashing e verificação de senhas usando bcrypt."""
from __future__ import annotations

import logging
from typing import Optional

import bcrypt

logger = logging.getLogger(__name__)


class PasswordService:
    """
    Serviço de segurança para hashing e verificação de senhas.
    
    Usa bcrypt com salt rounds configurável.
    ✅ Seguro contra ataques de dicionário
    ✅ Resistente a GPU/hardware acceleration
    ✅ Salt único por hash
    """

    def __init__(self, rounds: int = 12):
        """
        Inicializa o serviço com número de rounds de hashing.
        
        Args:
            rounds: Número de rounds bcrypt (padrão: 12, produção: 12-14)
        """
        if rounds < 4 or rounds > 31:
            raise ValueError("Rounds deve estar entre 4 e 31")
        self.rounds = rounds

    def hash_password(self, password: str) -> str:
        """
        Faz hash de uma senha usando bcrypt.
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash seguro (bcrypt com salt)
            
        Raises:
            ValueError: Se a senha estiver vazia
        """
        if not password or not isinstance(password, str):
            raise ValueError("Senha inválida: deve ser uma string não vazia")
        
        if len(password) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")
        
        try:
            salt = bcrypt.gensalt(rounds=self.rounds)
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return hashed.decode("utf-8")
        except Exception as e:
            logger.error(f"Erro ao fazer hash da senha: {e}")
            raise RuntimeError("Erro ao processar senha")

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verifica se uma senha corresponde ao hash bcrypt.
        
        Args:
            password: Senha em texto plano
            hashed: Hash bcrypt armazenado
            
        Returns:
            True se a senha corresponde, False caso contrário
        """
        if not password or not hashed:
            return False
        
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                hashed.encode("utf-8")
            )
        except Exception as e:
            logger.error(f"Erro ao verificar senha: {e}")
            return False

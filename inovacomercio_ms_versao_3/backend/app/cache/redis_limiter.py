# -*- coding: utf-8 -*-
"""Rate limiting distribuído (Token Bucket) com Redis + script Lua.

Porte do middleware FastAPI para Flask: cliente Redis síncrono, EVALSHA com
recarga automática do script (NOSCRIPT) e fail-open com log quando o Redis
está indisponível.
"""
from __future__ import annotations

import logging
import math
import threading
import time
from functools import wraps
from pathlib import Path

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from backend.core.config import settings

try:
    import redis
    from redis.exceptions import NoScriptError
except ImportError:  # pacote ausente: rate limiting vira no-op com aviso
    redis = None
    NoScriptError = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)

MENSAGEM_LIMITE = (
    "Limite de requisições excedido. "
    "Proteção financeira ativada (Too Many Requests)."
)

LUA_PATH = Path(__file__).resolve().parent / "rate_limiter.lua"


def _log_warning(message: str) -> None:
    try:
        from flask import current_app

        current_app.logger.warning(message)
    except Exception:
        LOGGER.warning(message)


class RedisTokenBucketLimiter:
    def __init__(self, client, lua_source: str) -> None:
        self._client = client
        self._lua_source = lua_source
        self._sha: str | None = None
        self._lock = threading.Lock()

    def _script_sha(self) -> str:
        with self._lock:
            if self._sha is None:
                self._sha = self._client.script_load(self._lua_source)
            return self._sha

    def allow(
        self,
        identifier: str,
        requested: float = 1.0,
        max_tokens: float | None = None,
        refill_rate: float | None = None,
    ) -> tuple[bool, float]:
        max_tokens = settings.RATE_LIMIT_MAX_TOKENS if max_tokens is None else max_tokens
        refill_rate = settings.RATE_LIMIT_REFILL_RATE if refill_rate is None else refill_rate
        chave = f"ratelimit:{identifier}"
        argumentos = [max_tokens, refill_rate, time.time(), requested]

        try:
            sha = self._script_sha()
            try:
                resultado = self._client.evalsha(sha, 1, chave, *argumentos)
            except NoScriptError:
                with self._lock:
                    self._sha = None
                resultado = self._client.evalsha(self._script_sha(), 1, chave, *argumentos)
        except Exception as exc:
            _log_warning(f"Rate limiter indisponível, requisição liberada (fail-open): {exc}")
            return True, 0.0

        permitido, tokens = resultado
        return bool(permitido), float(tokens)


_limiter: RedisTokenBucketLimiter | None = None
_build_lock = threading.Lock()


def _build_limiter() -> RedisTokenBucketLimiter | None:
    if not settings.REDIS_ENABLED:
        return None
    if redis is None:
        _log_warning(
            "REDIS_ENABLED=true, mas o pacote 'redis' não está instalado; "
            "rate limiting desativado."
        )
        return None
    try:
        lua_source = LUA_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        _log_warning(f"Não foi possível ler {LUA_PATH}: {exc}; rate limiting desativado.")
        return None

    client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
        decode_responses=True,
        socket_connect_timeout=1.5,
        socket_timeout=1.5,
    )
    return RedisTokenBucketLimiter(client, lua_source)


def get_limiter() -> RedisTokenBucketLimiter | None:
    global _limiter
    if _limiter is None:
        with _build_lock:
            if _limiter is None:
                _limiter = _build_limiter()
    return _limiter


def _request_identity() -> str:
    try:
        identidade = get_jwt_identity()
    except Exception:
        identidade = None
    if identidade:
        return f"user:{identidade}"
    return f"ip:{request.remote_addr or 'desconhecido'}"


def rate_limit(max_tokens: float | None = None, refill_rate: float | None = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter = get_limiter()
            if limiter is None:
                return func(*args, **kwargs)

            permitido, _tokens = limiter.allow(
                _request_identity(), 1.0, max_tokens, refill_rate
            )
            if permitido:
                return func(*args, **kwargs)

            taxa = settings.RATE_LIMIT_REFILL_RATE if refill_rate is None else refill_rate
            espera = max(1, math.ceil(1 / taxa)) if taxa > 0 else 60
            resposta = jsonify({"error": MENSAGEM_LIMITE})
            resposta.status_code = 429
            resposta.headers["Retry-After"] = str(espera)
            return resposta

        return wrapper

    return decorator

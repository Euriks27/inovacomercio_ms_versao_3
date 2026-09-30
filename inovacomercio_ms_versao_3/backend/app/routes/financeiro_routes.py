# -*- coding: utf-8 -*-
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from backend.schemas.financeiro import TransacaoCreate
from backend.services import financeiro_service

bp = Blueprint("financeiro", __name__, url_prefix="/api/v1/financeiro")


@bp.get("/transacoes")
@jwt_required()
def listar():
    return jsonify(financeiro_service.listar_transacoes().model_dump())


@bp.post("/transacao")
@jwt_required()
def criar():
    try:
        payload = TransacaoCreate(**(request.get_json() or {}))
    except Exception as exc:
        return jsonify({"error": f"Payload inválido: {exc}"}), 400

    return jsonify(
        financeiro_service.criar_transacao(payload).model_dump()
    ), 201
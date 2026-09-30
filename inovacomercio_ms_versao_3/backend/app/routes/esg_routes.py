# -*- coding: utf-8 -*-
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from backend.schemas.esg import LogisticaReversaRequest
from backend.services import esg_service

bp = Blueprint("esg", __name__, url_prefix="/api/v1/esg")


@bp.get("/logistica")
@jwt_required()
def historico():
    return jsonify(esg_service.historico_logistica().model_dump())


@bp.post("/logistica")
@jwt_required()
def registrar():
    try:
        payload = LogisticaReversaRequest(**(request.get_json() or {}))
    except Exception as exc:
        return jsonify({"error": f"Payload inválido: {exc}"}), 400

    return jsonify(
        esg_service.registrar_logistica_reversa(payload).model_dump()
    ), 201
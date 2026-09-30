# -*- coding: utf-8 -*-
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from backend.schemas.pdv import PdvVendaRequest
from backend.services import pdv_service

bp = Blueprint("pdv", __name__, url_prefix="/api/v1/pdv")


@bp.post("/venda")
@jwt_required()
def registrar_venda():
    try:
        payload = PdvVendaRequest(**(request.get_json() or {}))
    except Exception as exc:
        return jsonify({"error": f"Payload inválido: {exc}"}), 400

    try:
        resultado = pdv_service.processar_venda(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(resultado.model_dump()), 201
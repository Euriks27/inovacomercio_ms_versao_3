# -*- coding: utf-8 -*-
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from backend.schemas.estoque import (
    MovimentacaoRequest,
    ProdutoCreate,
    ProdutoUpdate,
)
from backend.services import estoque_service

bp = Blueprint("estoque", __name__, url_prefix="/api/v1/estoque")


@bp.get("")
@jwt_required()
def listar():
    return jsonify([p.model_dump() for p in estoque_service.listar_estoque()])


@bp.post("/produto")
@jwt_required()
def criar():
    try:
        payload = ProdutoCreate(**(request.get_json() or {}))
    except Exception as exc:
        return jsonify({"error": f"Payload inválido: {exc}"}), 400

    return jsonify(estoque_service.criar_produto(payload).model_dump()), 201


@bp.put("/produto/<int:product_id>")
@jwt_required()
def atualizar(product_id: int):
    try:
        payload = ProdutoUpdate(**(request.get_json() or {}))
    except Exception as exc:
        return jsonify({"error": f"Payload inválido: {exc}"}), 400

    try:
        return jsonify(
            estoque_service.atualizar_produto(product_id, payload).model_dump()
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404


@bp.delete("/produto/<int:product_id>")
@jwt_required()
def remover(product_id: int):
    try:
        estoque_service.remover_produto(product_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    return "", 204


@bp.post("/movimentacao")
@jwt_required()
def movimentar():
    try:
        payload = MovimentacaoRequest(**(request.get_json() or {}))
    except Exception as exc:
        return jsonify({"error": f"Payload inválido: {exc}"}), 400

    try:
        estoque_service.movimentar(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({"status": "ok"}), 201
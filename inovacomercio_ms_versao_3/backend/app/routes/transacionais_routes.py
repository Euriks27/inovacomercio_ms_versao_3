# -*- coding: utf-8 -*-
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from backend.core.database import db

transacionais_bp = Blueprint("transacionais", __name__, url_prefix="/api/v1")

@transacionais_bp.route("/pdv/venda", methods=["POST"])
@jwt_required()
def realizar_venda():
    dados = request.get_json() or {}
    itens = dados.get("itens", [])
    total = dados.get("total", 0.0)
    
    if not itens:
        return jsonify({"erro": "O carrinho está vazio"}), 400
        
    # Lógica transacional simulada/gravada
    return jsonify({
        "status": "sucesso",
        "mensagem": "Venda processada com sucesso no PDV",
        "total_pago": total,
        "itens_processados": len(itens)
    }), 200

@transacionais_bp.route("/estoque", methods=["GET"])
@jwt_required()
def listar_estoque():
    # Retorna o inventário atualizado
    return jsonify([
        {"id": 1, "sku": "7891000", "produto": "Arroz Tio João 5kg", "qtd": 45, "min": 10},
        {"id": 2, "sku": "7892000", "produto": "Feijão Carioca 1kg", "qtd": 30, "min": 8},
        {"id": 3, "sku": "7893000", "produto": "Óleo de Soja 900ml", "qtd": 12, "min": 15}
    ]), 200

@transacionais_bp.route("/financeiro/transacoes", methods=["GET"])
@jwt_required()
def listar_transacoes_financeiras():
    return jsonify([
        {"data": "2026-04-01", "tipo": "receita", "desc": "Venda PDV (Terminal 01)", "valor": 1250.50},
        {"data": "2026-04-01", "tipo": "despesa", "desc": "Reposição de Estoque", "valor": 450.00}
    ]), 200

@transacionais_bp.route("/logistica-reversa", methods=["POST"])
@jwt_required()
def registrar_logistica_reversa():
    dados = request.get_json() or {}
    material = dados.get("material", "PET")
    peso = dados.get("peso_kg", 0.0)
    
    credito_gerado = peso * 0.15 # Fator ESG simulado
    return jsonify({
        "status": "sucesso",
        "material": material,
        "peso_kg": peso,
        "credito_verde_gerado": credito_gerado,
        "mensagem": "Logística reversa registada com sucesso para pontuação ESG."
    }), 200
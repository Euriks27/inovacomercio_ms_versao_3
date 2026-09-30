# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
)
from pydantic import BaseModel, Field

# ✅ Instância única do db
from backend.app.database import db

# ✅ Models extraídos
from backend.app.models import AuditLog, Product


# ============================================================================
# CONFIGURAÇÃO FLASK
# ============================================================================

app = Flask(__name__)

app.config.update(
    SECRET_KEY="inovacomercio-secret",
    JWT_SECRET_KEY="inovacomercio-jwt-secret",
    SQLALCHEMY_DATABASE_URI="sqlite:///inovacomercio.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "http://localhost:8501",
        ],
        "allow_headers": ["Content-Type", "Authorization", "X-Tenant-Id"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    }
})

jwt = JWTManager(app)

# ✅ Registra a instância única de db no app
db.init_app(app)


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class HealthCheckResponse(BaseModel):
    status: str
    ambiente: str
    tenant_padrao: str


class User(BaseModel):
    nome: str
    email: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    expires_in: int
    usuario: User
    tenant_id: str


class DashboardResumoResponse(BaseModel):
    faturamento_mes: float = Field(ge=0)
    ticket_medio: float = Field(ge=0)
    margem_media: float = Field(ge=0)
    rupturas_ativas: int
    credito_verde_saldo: float = Field(ge=0)
    variacao_mom: float


class CurvaABCItem(BaseModel):
    codigo: str
    produto: str
    faturamento: float = Field(ge=0)
    curva: str
    participacao: float = Field(ge=0)


class CurvaABCClass(BaseModel):
    classe: str
    faturamento: float = Field(ge=0)


class CurvaABCResponse(BaseModel):
    top10: List[CurvaABCItem]
    classes: List[CurvaABCClass]


class EsgAmbiental(BaseModel):
    co2_evitado_kg: float = Field(ge=0)
    residuos_kg: float = Field(ge=0)


class EsgSocial(BaseModel):
    colaboradores: int


class EsgGovernanca(BaseModel):
    conformidade_pct: float = Field(ge=0, le=1)


class EsgIndicadoresResponse(BaseModel):
    ambiental: EsgAmbiental
    social: EsgSocial
    governanca: EsgGovernanca


class AuditoriaEvento(BaseModel):
    id: int
    usuario: str
    evento: str
    modulo: str
    ts: int


class ScannerFeedback(BaseModel):
    tipo: str
    som: str
    cor: str
    vibracao_ms: int
    mensagem: str
    auto_clear_ms: int


class ScannerProduct(BaseModel):
    id: int
    sku: str
    nome: str
    unidade: str
    preco_venda: float
    estoque_atual: int
    estoque_minimo: int
    abaixo_minimo: bool
    fator_conversao: int


class ScannerCodigo(BaseModel):
    original: str
    normalizado: str
    tipo: str


class ScannerResponse(BaseModel):
    feedback: ScannerFeedback
    codigo: ScannerCodigo
    produtos: List[ScannerProduct]
    event_id: str
    audit_id: int


# ============================================================================
# DADOS INICIAIS (SEED)
# ============================================================================

def _seed_database() -> None:
    """Popula o banco apenas se estiver vazio."""

    if Product.query.count() == 0:
        db.session.add_all([
            Product(
                produto="Vinho Tinto Reservado 750ml",
                categoria="Bebidas",
                custo=25.00, markup=1.60,
                preco_sugerido=40.00, margem=0.375,
                estoque_atual=35, estoque_minimo=10,
            ),
            Product(
                produto="Cerveja Artesanal IPA 500ml",
                categoria="Bebidas",
                custo=8.50, markup=1.70,
                preco_sugerido=14.45, margem=0.410,
                estoque_atual=6, estoque_minimo=8,
            ),
            Product(
                produto="Queijo Gouda Artesanal 250g",
                categoria="Frios",
                custo=18.00, markup=1.65,
                preco_sugerido=29.70, margem=0.393,
                estoque_atual=22, estoque_minimo=10,
            ),
            Product(
                produto="Café Gourmet Orgânico 500g",
                categoria="Mercearia",
                custo=30.00, markup=1.20,
                preco_sugerido=36.00, margem=0.167,
                estoque_atual=3, estoque_minimo=12,
            ),
        ])

    if AuditLog.query.count() == 0:
        db.session.add_all([
            AuditLog(usuario="Admin", evento="LOGIN",
                     modulo="AUTH", ts=1725450000),
            AuditLog(usuario="Admin", evento="VERIFICACAO_CERTIFICADO",
                     modulo="FISCAL", ts=1725451200),
            AuditLog(usuario="Gestor", evento="SCAN_REALIZADO",
                     modulo="SCANNER", ts=1725452400),
        ])

    db.session.commit()


with app.app_context():
    db.create_all()
    _seed_database()


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

VALID_USERS = {
    "gestor@inovacomercio.ms": "123456",
    "admin@inovacomercio.ms": "admin123",
}


# ============================================================================
# ROTAS
# ============================================================================

@app.get("/")
def index():
    return jsonify({
        "sistema": "InovaComércio MS",
        "versao": "6.0",
        "status": "online",
    })


@app.get("/api/v1/health")
def health_check():
    return jsonify(
        HealthCheckResponse(
            status="online",
            ambiente="local",
            tenant_padrao="demo_ms",
        ).model_dump()
    )


@app.post("/api/v1/auth/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    senha = data.get("senha")

    if VALID_USERS.get(email) != senha:
        return jsonify({"error": "Credenciais inválidas"}), 401

    token = create_access_token(identity=email)

    return jsonify(
        LoginResponse(
            access_token=token,
            expires_in=3600,
            usuario=User(
                nome="Gestor InovaComércio MS",
                email=email,
                role="admin",
            ),
            tenant_id="demo_ms",
        ).model_dump()
    )


@app.get("/api/v1/dashboard/resumo")
@jwt_required()
def dashboard_resumo():
    return jsonify(
        DashboardResumoResponse(
            faturamento_mes=482350.75,
            ticket_medio=87.42,
            margem_media=0.284,
            rupturas_ativas=14,
            credito_verde_saldo=3280.50,
            variacao_mom=0.071,
        ).model_dump()
    )


@app.get("/api/v1/precificacao")
@jwt_required()
def precificacao():
    produtos = Product.query.all()
    return jsonify([p.to_dict() for p in produtos])


@app.get("/api/v1/curva-abc")
@jwt_required()
def curva_abc():
    return jsonify(
        CurvaABCResponse(
            top10=[
                CurvaABCItem(codigo="P001", produto="Vinho Tinto Reservado 750ml",
                             faturamento=145000, curva="A", participacao=30),
                CurvaABCItem(codigo="P002", produto="Cerveja Artesanal IPA 500ml",
                             faturamento=98000, curva="A", participacao=20.3),
            ],
            classes=[
                CurvaABCClass(classe="A", faturamento=243000),
                CurvaABCClass(classe="B", faturamento=110000),
                CurvaABCClass(classe="C", faturamento=129350.75),
            ],
        ).model_dump()
    )


@app.get("/api/v1/esg/indicadores")
@jwt_required()
def esg_indicadores():
    return jsonify(
        EsgIndicadoresResponse(
            ambiental=EsgAmbiental(co2_evitado_kg=1420.5, residuos_kg=450),
            social=EsgSocial(colaboradores=24),
            governanca=EsgGovernanca(conformidade_pct=0.98),
        ).model_dump()
    )


@app.get("/api/v1/auditoria/eventos")
@jwt_required()
def auditoria_eventos():
    logs = AuditLog.query.all()
    return jsonify([
        AuditoriaEvento(
            id=log.id, usuario=log.usuario, evento=log.evento,
            modulo=log.modulo, ts=log.ts,
        ).model_dump()
        for log in logs
    ])


@app.post("/api/v1/scanner/scan")
@jwt_required()
def scanner_scan():
    data = request.get_json() or {}
    codigo = data.get("codigo", "7891000100102")

    estoque_baixo = (codigo == "7891000100102")

    return jsonify(
        ScannerResponse(
            feedback=ScannerFeedback(
                tipo="WARNING" if estoque_baixo else "SUCCESS",
                som="warning" if estoque_baixo else "success",
                cor="amarelo" if estoque_baixo else "verde",
                vibracao_ms=60 if estoque_baixo else 40,
                mensagem=(
                    "Atenção: Estoque próximo ao mínimo!"
                    if estoque_baixo
                    else "Produto localizado"
                ),
                auto_clear_ms=2000,
            ),
            codigo=ScannerCodigo(
                original=codigo, normalizado=codigo, tipo="EAN13",
            ),
            produtos=[
                ScannerProduct(
                    id=1,
                    sku="SKU-VINHO-01",
                    nome="Vinho Tinto Reservado 750ml",
                    unidade="UN",
                    preco_venda=40.00,
                    estoque_atual=5 if estoque_baixo else 150,
                    estoque_minimo=10,
                    abaixo_minimo=estoque_baixo,
                    fator_conversao=1,
                )
            ],
            event_id="evt-demo-001",
            audit_id=99,
        ).model_dump()
    )


# ============================================================================
# ENTRADA
# ============================================================================

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
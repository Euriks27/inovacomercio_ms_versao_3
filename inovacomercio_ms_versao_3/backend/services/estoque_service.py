# -*- coding: utf-8 -*-
from __future__ import annotations

from backend.database import db
from backend.models.product import Product
from backend.models.stock_movement import StockMovement
from backend.schemas.estoque import (
    MovimentacaoRequest,
    ProdutoCreate,
    ProdutoEstoque,
    ProdutoUpdate,
)


def _calcular_cobertura(estoque: int, minimo: int) -> int:
    """Cobertura estimada em dias (heurística: 3x o mínimo = 1 mês)."""
    if minimo <= 0:
        return 999
    return max(0, int((estoque / (minimo / 3)) + 1))


def _to_estoque(p: Product) -> ProdutoEstoque:
    estoque_atual = getattr(p, "estoque_atual", 0) or 0
    estoque_minimo = getattr(p, "estoque_minimo", 5) or 5

    return ProdutoEstoque(
        id=p.id,
        sku=f"SKU-{p.id:04d}",
        produto=p.produto,
        categoria=getattr(p, "categoria", "Mercearia") or "Mercearia",
        custo=p.custo,
        preco_sugerido=p.preco_sugerido,
        margem=p.margem,
        estoque_atual=estoque_atual,
        estoque_minimo=estoque_minimo,
        ponto_pedido=estoque_minimo + 5,
        cobertura_dias=_calcular_cobertura(estoque_atual, estoque_minimo),
        abaixo_minimo=estoque_atual < estoque_minimo,
    )


def listar_estoque() -> list[ProdutoEstoque]:
    produtos = Product.query.order_by(Product.produto).all()
    return [_to_estoque(p) for p in produtos]


def criar_produto(payload: ProdutoCreate) -> ProdutoEstoque:
    preco = payload.custo * payload.markup
    margem = (preco - payload.custo) / preco if preco > 0 else 0.0

    p = Product(
        produto=payload.produto,
        custo=payload.custo,
        markup=payload.markup,
        preco_sugerido=round(preco, 2),
        margem=round(margem, 4),
    )
    # Campos opcionais (se o model já os tiver; senão, apenas ignorados)
    if hasattr(p, "categoria"):
        p.categoria = payload.categoria
    if hasattr(p, "estoque_atual"):
        p.estoque_atual = payload.estoque_atual
    if hasattr(p, "estoque_minimo"):
        p.estoque_minimo = payload.estoque_minimo

    db.session.add(p)
    db.session.commit()
    return _to_estoque(p)


def atualizar_produto(product_id: int, payload: ProdutoUpdate) -> ProdutoEstoque:
    p = Product.query.get(product_id)
    if p is None:
        raise ValueError("Produto não encontrado")

    if payload.produto is not None:
        p.produto = payload.produto
    if payload.custo is not None:
        p.custo = payload.custo
    if payload.markup is not None:
        p.markup = payload.markup

    p.preco_sugerido = round(p.custo * p.markup, 2)
    p.margem = round((p.preco_sugerido - p.custo) / p.preco_sugerido, 4) \
        if p.preco_sugerido > 0 else 0.0

    if payload.categoria is not None and hasattr(p, "categoria"):
        p.categoria = payload.categoria
    if payload.estoque_atual is not None and hasattr(p, "estoque_atual"):
        p.estoque_atual = payload.estoque_atual
    if payload.estoque_minimo is not None and hasattr(p, "estoque_minimo"):
        p.estoque_minimo = payload.estoque_minimo

    db.session.commit()
    return _to_estoque(p)


def remover_produto(product_id: int) -> None:
    p = Product.query.get(product_id)
    if p is None:
        raise ValueError("Produto não encontrado")
    db.session.delete(p)
    db.session.commit()


def movimentar(payload: MovimentacaoRequest) -> None:
    p = Product.query.get(payload.product_id)
    if p is None:
        raise ValueError("Produto não encontrado")

    delta = payload.quantidade
    if payload.tipo == "SAIDA":
        if getattr(p, "estoque_atual", 0) < delta:
            raise ValueError("Estoque insuficiente para saída")
        delta = -delta
    elif payload.tipo == "ENTRADA":
        pass  # delta positivo
    else:  # AJUSTE
        if hasattr(p, "estoque_atual"):
            p.estoque_atual = delta
            db.session.add(
                StockMovement(
                    product_id=p.id,
                    tipo="AJUSTE",
                    quantidade=delta,
                    motivo=payload.motivo,
                )
            )
            db.session.commit()
            return

    if hasattr(p, "estoque_atual"):
        p.estoque_atual = (p.estoque_atual or 0) + delta

    db.session.add(
        StockMovement(
            product_id=p.id,
            tipo=payload.tipo,
            quantidade=payload.quantidade,
            motivo=payload.motivo,
        )
    )
    db.session.commit()
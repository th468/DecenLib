---
name: django-advanced-guide
description: Djangoの標準機能（ORM最適化、トランザクション、Manager等）を深く理解し、中級者以上の実装パターンを適用するための技術ガイド。
---

# Django Advanced Guide

## 概要
Djangoの標準機能（ORM, Middleware, Signals等）を深く理解し、中級者以上の実装パターンを適用するためのガイドです。

## 指導トピック
1. **ORMの最適化 (N+1問題の回避)**:
   `ListView` や QuerySet 操作において、`select_related` や `prefetch_related` が必要ないか常に検証する。
2. **ビジネスロジックの配置**:
   Viewを薄く保ち、ロジックを Model, Manager, Form, または Service 層に適切に分散させる設計を提案する。
3. **トランザクション管理**:
   データの整合性が重要な処理（貸出・返却など）において、`transaction.atomic()` と適切なロック戦略を指導する。
4. **Custom Manager/QuerySet**:
   `Lending.objects.active()` のような, ドメイン特化型のクエリ操作の構築を推奨する。

## 推奨パターン
- Fat Model / Thin View
- Service Layer (複数のモデルを跨ぐ複雑な処理)
- Mixins による共通処理の共通化

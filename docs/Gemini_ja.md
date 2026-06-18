## 日本語訳・詳細解説 (Human-Readable Appendix)
<aside>
このセクションは開発者向けの参照用です。AIは上記の英語セクションを絶対的な指示として遵守してください。

### 1. プロジェクトの概要と目的
- **目標:** キャリアポートフォリオ。架空の会社のための分散型図書館アプリケーションのプロトタイプ。
- **課題:** 物理的な移動なしに、20フロアにわたる15,000冊を「仮想本棚」で管理すること。
- **UX制約:** 持ち出し防止とデータ整合性のため、場所の詳細は貸出または予約確定後にのみ表示されなければならない（MUST）。

### 2. ディレクトリ構成
- `library/`: プロジェクトルート。
  - `core/`: 抽象基盤。全アプリの共通規約。
  - `accounts/`: 認証、部署管理、権限。
  - `catalog/`: 静的データ（書誌、蔵書、場所、お気に入り）。
  - `transactions/`: 動的ライフサイクル（貸出・予約ロジック）。ミッションクリティカル。
  - `dashboard/`: 統合ポータルUI。アプリを跨いだデータの可視化。

### 3. 技術スタック
(Django 6.0.2, Python 3.14, Ruff, mypy 等を使用)

### 4. エンジニアリング基準
#### モデルとロジック
- **BaseModel継承:** 全モデルは `is_active` による論理削除を標準化するため `core.models.BaseModel` を継承しなければならない（MUST）。
- **ロジック配置:** 1.Model (Fat Model) > 2.Form > 3.Service の順に優先。Viewにビジネスロジックを実装してはならない（DO NOT / Thin View）。
- **データリセット:** Seed Dataなどのメンテナンススクリプトでは、レコードの物理削除に `all_objects.hard_delete()` を使用すること。標準の `.delete()` は論理削除を行うのみであり、ユニーク制約を持つフィールドの再投入時に `IntegrityError` を引き起こす原因となる。
- **型安全性:** `timedelta` は常に `datetime` からインポートすること。Viewで `request.user` にアクセスする際は、mypyによる型安全性を確保するため、`LoginRequiredMixin` が存在する場合でも明示的に `is_authenticated` チェックを行うこと。
- **命名:** PEP8に厳格に準拠（クラスは PascalCase、変数・関数は snake_case）。

#### テスト
- **Factory:** `factories.py` は必須（MANDATORY）。`BaseModelTestMixin` を使用して論理削除と `__str__` を厳密に検証すること。
- **Factoryにおける多対多:** `ManyToManyField` を持つモデルには、Seed Data作成時にシームレスなリレーション構築を可能にするため、`@factory.post_generation` を使用すること。
- **網羅性:** 正常系、境界値、エラーハンドリングを含めること。

#### テンプレート
- `common/base.html` を継承。DRY原則のためUI部品は `common/includes/` でモジュール化すること。

### 5. 運用プロトコル
- **TODO管理:** 実装中に発見した技術的負債や将来の改善案は、必ず `docs/TODO.md` に記録しなければならない（MUST）。
- **設計の文書化:** 重要な設計判断、パフォーマンスの最適化、および技術的な根拠（Mixinの階層化、N+1の解決策など）は、設計の透明性と知識移転を確保するため、必ず `docs/ARCH_DESIGN.md` に文書化しなければならない（MUST）。
- **構造優先:** 局所的な修正よりも、構造的またはデータモデルの問題の解決を優先すること。

### 6. 主要コマンド
- テスト: `python library/manage.py test library`
- Quality: `ruff check .` / `mypy .`
- データベース: `python library/manage.py makemigrations` / `migrate`

### 7. セッション終了プロトコル
- **まとめ形式:** ユーザーから明示的な指示があった際に、成果の簡潔な要約を提供すること。
    - **要約（一行）:** その日の核心的な成果を 30 文字以内で記述する。
    - **個別項目:** 具体的な技術的マイルストーンや成果を 3〜5 つの箇条書きで記述する。
</aside>

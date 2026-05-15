# Project Instructions: Libarally

# Project Instructions: Libarally

## 0. プロジェクトの背景と目的
- **ポートフォリオ:** このプロジェクトは就職活動のためのポートフォリオとして作成されています。
- **学習目的:** プログラミングスキルの向上、および開発ツールの効果的な活用方法を学習することを主眼に置いています。
- **設定:** 架空の会社からの依頼を受け、プロフェッショナルな品質で開発・納品するシミュレーションとして進行します。

## 1. プロジェクトの概要
- **名称:** Libarally
- **目的:** 蔵書の管理、ユーザーアカウント管理、および貸出（transactions）の管理を行うプロトタイプ。
- **主要な機能:**
  - `accounts`: カスタムユーザーモデル、ユーザー認証、部署（Department）管理。
  - `books`: 書籍情報（Biblio）および実体（Book）の管理。
  - `transactions`: 貸出（Lending）及び予約プロセスの管理。
  - `dashboard`: 管理者・利用者向けのダッシュボード。
  - `core`: プロジェクト全体で共有する基本クラス（BaseModel）やMixin。

## 2. 技術スタック
- **Framework:** Django 6.0.2
- **Language:** Python 3.14
- **Forms:** django-widget-tweaks
- **Testing:** Factory Boy, Faker (Django標準のTestCaseを使用)
- **Database:** SQLite3 (開発用)

## 3. ディレクトリ構成
- `libarally/`: Django プロジェクトルート
  - `manage.py`: エントリポイント
  - `libarally/`: プロジェクト設定（settings.py, urls.py）
  - `accounts/`, `books/`, `transactions/`, `dashboard/`: 各機能アプリ
  - `core/`: 共通モデル・ミキシン
  - `templates/`: 全体共有テンプレート
    - `common/`: ベースレイアウトや共通パーツ

## 4. 開発・コーディング規約
### モデル
- `core.models.BaseModel` を可能な限り継承し、作成日時・更新日時の管理を一貫させる。
- 論理削除（is_active 等）のパターンが `books` アプリなどで見られるため、それに倣う。

### テスト
- 各アプリの `tests/` ディレクトリ内にテストコードを配置する。
- テストデータの作成には `factories.py` で定義された Factory クラスを使用する。
- 新機能追加時は必ずテストコードを更新・追加すること。

### テンプレート
- `templates/common/base.html` をベースとし、`block` を適切に使用して拡張する。
- UI部品の共通化には `templates/common/includes/` を活用する。

## 5. 主要なコマンド
- **サーバー起動:** `python libarally/manage.py runserver`
- **テスト実行:** `python libarally/manage.py test libarally`
- **マイグレーション作成:** `python libarally/manage.py makemigrations`
- **マイグレーション適用:** `python libarally/manage.py migrate`

## 6. コミュニケーションと言行
- **変更提案のプロセス:**
  - コードを実際に変更する前に、修正が必要な箇所を一覧化し、その理由（Rationale）を説明すること。
  - 局所的な修正よりも先に、構造上の問題（設計、データ構造、アーキテクチャ）がないかを確認し、問題がある場合はまずそれを報告すること。
- **代替案の提示:**
  - 構造上の問題を指摘する際は、必ず代替案（リファクタリング案）を提示すること。
  - 代替案は必ずしも具体的なコードである必要はなく、概念的な方向性の提示でもよい。
  - 可能であれば複数の案を提示すること。ただし、採用の可能性が著しく低いと思われる場合は、最も推奨される1案のみで構わない。

## 7. 学習と品質のための追加ルール
- **技術選定の解説:** 新しい手法やライブラリを提案する際は、学習目的のため、そのメリット・デメリットを比較・解説すること。
- **不足情報の確認:** コンテキストや要件が不足している、あるいは曖昧だと判断した場合は、推測で進めず、作業前に必ずユーザーに質問して解消すること。
- **TODO管理:** 実装時に発見した「将来的な改善点」や「技術的負債」は、別途 `TODO.md` に記録、またはコード内に明記すること。

## 8. 依頼主（架空）の要件詳細
(ここに依頼内容の要約を記述してください)


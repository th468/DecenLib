# Astral公式のuv統合済みPython 3.12軽量イメージ
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# コンテナ内の作業ディレクトリ
WORKDIR /app

# Pythonの出力バッファリングを無効化し、ログを即時出力
ENV PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# 依存関係定義ファイルを先にコピー（キャッシュ有効化）
COPY pyproject.toml uv.lock* /app/

# uvを使って依存関係をインストール
RUN uv sync --frozen --no-install-project

# アプリケーションコード全体をコピー
COPY . /app/

# ポートの開放
EXPOSE 8000

# 本番用 Web サーバー起動コマンド (Gunicorn)
CMD ["sh", "-c", "uv run python library/manage.py collectstatic --noinput && uv run gunicorn --chdir library config.wsgi:application --bind 0.0.0.0:$PORT]

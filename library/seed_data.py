import os
import random

import django
from django.db import connection

# Djangoの設定をロード
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.factories import DepartmentFactory, UserFactory  # noqa: E402
from accounts.models import User  # noqa: E402
from catalog.factories import (  # noqa: E402
    BiblioFactory,
    BookFactory,
    FloorFactory,
    ShelfFactory,
)
from catalog.models import Biblio, Book, Category, Floor, Shelf  # noqa: E402
from transactions.factories import LendingFactory, ReservationFactory  # noqa: E402
from transactions.models import Lending, Reservation  # noqa: E402


def clean_and_seed():
    print("=== 全データを一掃し、クリーンな再投入を開始します ===")

    # 1. 外部キー制約を一時的に無視して全削除 (SQLite用)
    # BaseModelの仕様により objects は active なデータのみを対象とするため、
    # 論理削除済みのデータも含めて物理削除するには all_objects.hard_delete() を使用する。
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = OFF;")

        print("既存データを一括削除中...")
        Lending.all_objects.hard_delete()
        Reservation.all_objects.hard_delete()
        Book.all_objects.hard_delete()
        Biblio.all_objects.hard_delete()
        Category.all_objects.hard_delete()
        Shelf.all_objects.hard_delete()
        Floor.all_objects.hard_delete()
        User.objects.exclude(email="admin@example.com").delete()

        cursor.execute("PRAGMA foreign_keys = ON;")

    # 2. 基礎データの作成
    print("基礎データを再構築中...")

    # 管理者
    admin, created = User.objects.get_or_create(
        email="admin@example.com",
        defaults={
            "em_num": "ADMIN001",
            "is_staff": True,
            "is_superuser": True,
            "name": "管理者 太郎",
        },
    )
    if created:
        admin.set_password("password123")
        admin.save()
        print("  - 管理者ユーザーを作成しました: admin@example.com / password123")

    # 部署
    depts = DepartmentFactory.create_batch(5)
    print(f"  - 部署を {len(depts)} 件作成しました。")

    # カテゴリ
    category_names = ["IT・技術書", "ビジネス・経済", "デザイン・アート", "小説・文芸", "雑誌"]
    categories = [Category.objects.create(name=name) for name in category_names]
    print(f"  - カテゴリを {len(categories)} 件作成しました。")

    # フロアと棚
    floors = FloorFactory.create_batch(3)
    shelves = []
    for floor in floors:
        shelves.extend(ShelfFactory.create_batch(3, floor=floor))
    print(f"  - フロア {len(floors)} 件、棚 {len(shelves)} 件を作成しました。")

    # 一般ユーザー
    users = UserFactory.create_batch(10, department=random.choice(depts))
    print(f"  - 一般ユーザーを {len(users)} 件作成しました。")

    # 3. 本の作成
    print("書籍データを生成中...")
    biblios = []
    for _ in range(50):
        biblio = BiblioFactory()
        # カテゴリをランダムに1〜2個紐付け
        biblio.categories.set(random.sample(categories, random.randint(1, 2)))
        biblios.append(biblio)

        # 各書誌に対して1〜3冊の蔵書(Book)を作成
        for _ in range(random.randint(1, 3)):
            BookFactory(biblio=biblio, shelf=random.choice(shelves))

    print(f"  - 書誌 {Biblio.objects.count()} 件、蔵書 {Book.objects.count()} 件を作成しました。")

    # 4. トランザクションデータの作成 (貸出・予約)
    print("トランザクションデータを生成中...")

    # 貸出中データ
    available_books = list(Book.objects.filter(status=Book.Status.AVAILABLE))
    lending_count = min(len(available_books), 15)
    for _ in range(lending_count):
        book = available_books.pop()
        LendingFactory(book=book, user=random.choice(users), status=Lending.Status.LENDING)

    # 予約データ
    for _ in range(10):
        ReservationFactory(
            user=random.choice(users),
            biblio=random.choice(biblios),
            status=Reservation.Status.WAITING
        )

    print(f"  - 貸出 {Lending.objects.count()} 件、予約 {Reservation.objects.count()} 件を作成しました。")

    print("\n=== 完了しました！ ===")
    print(f"Books: {Book.objects.count()}, Biblios: {Biblio.objects.count()}")
    print(f"Users: {User.objects.count()}, Transactions: {Lending.objects.count() + Reservation.objects.count()}")
    print("ログイン: admin@example.com / password123")


if __name__ == "__main__":
    clean_and_seed()

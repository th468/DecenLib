from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Floor, Shelf

class FloorShelfTest(TestCase):

    def setUp(self):
        """テストデータの準備"""
        # 1. 階情報を作成
        self.floor_1f = Floor.objects.create(name="1階")
        
        # 2. 本棚情報を作成
        self.shelf_a = Shelf.objects.create(
            name="本棚A",
            floor=self.floor_1f
        )

    def test_floor_creation(self):
        """Floorが正しく作成され、名前が取得できるか"""
        self.assertEqual(self.floor_1f.name, "1階")

    def test_shelf_creation(self):
        """Shelfが正しく作成され、Floorと紐付いているか"""
        self.assertEqual(self.shelf_a.name, "本棚A")
        self.assertEqual(self.shelf_a.floor.name, "1階")

    def test_floor_reverse_relationship(self):
        """related_name='shelf' を使って、FloorからShelfを逆参照できるか"""
        # 1階に属する本棚をすべて取得
        shelves = self.floor_1f.shelf.all()
        self.assertIn(self.shelf_a, shelves)
        self.assertEqual(shelves.count(), 1)

    def test_shelf_on_delete_protect(self):
        """Floorを削除しようとした際、紐づくShelfがあるためPROTECTされるか"""
        with self.assertRaises(IntegrityError):
            # 実際にはDBの種類により ProtectedError か IntegrityError が発生します
            # Djangoの ProtectedError を補足する場合は from django.db.models import ProtectedError が必要
            self.floor_1f.delete()

from django.test import TestCase
from django.db.models import ProtectedError
from .models import Floor, Shelf, Biblio, Book


class BookRelationshipTest(TestCase):

    def setUp(self):
        """テストデータの準備"""
        # 階と棚の準備
        self.floor = Floor.objects.create(name="2階")
        self.shelf = Shelf.objects.create(name="棚B1", floor=self.floor)

        # 1. 書誌情報を作成
        self.biblio = Biblio.objects.create(
            isbn="9784123456789",
            title="Django実践ガイド",
            author="エンジニア太郎",
            publisher="技術出版",
            # price = 3000 ()を付けてモデルを修正済みと想定
        )

        # 2. 蔵書（実物）を2冊作成
        self.book_1 = Book.objects.create(isbn=self.biblio, shelf=self.shelf, count=1)
        self.book_2 = Book.objects.create(isbn=self.biblio, shelf=self.shelf, count=2)

    def test_biblio_content(self):
        """書誌情報が正しく保存されているか"""
        self.assertEqual(self.biblio.title, "Django実践ガイド")
        self.assertTrue(self.biblio.is_available) # デフォルト値の確認

    def test_book_str(self):
        """Bookの__str__が書誌のタイトルを返すか"""
        # 修正後のモデル定義に従い、BookからBiblioのタイトルを参照
        self.assertEqual(str(self.book_1), "Django実践ガイド")

    def test_book_absolute_url(self):
        """get_absolute_urlが正しいパスを返すか"""
        # urls.pyで name="model_detail" と設定されている前提
        expected_url = f"/model_detail/{self.book_1.pk}/" # 実際のURL構造に合わせる
        # まだurls.pyが未完成なら、ここが失敗する可能性があるので注意
        self.assertEqual(self.book_1.get_absolute_url(), expected_url)

    def test_biblio_reverse_relationship(self):
        """1つのBiblioに複数のBookが紐づいているか（逆参照）"""
        # related_name="book" を使用
        books_count = self.biblio.book.count()
        self.assertEqual(books_count, 2)

    def test_biblio_delete_protection(self):
        """蔵書がある状態で書誌情報を削除しようとするとブロックされるか"""
        with self.assertRaises(ProtectedError):
            self.biblio.delete()
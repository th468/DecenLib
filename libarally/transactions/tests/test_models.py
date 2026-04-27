from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import IntegrityError
from accounts.factories import UserFactory
from books.factories import BookFactory
from ..models import Lending
from ..factories import LendingFactory

class LendingManagerTest(TestCase):
    """
    LendingManager のカスタムメソッド（lend, collect, renew）をテストするクラス
    ※ Factoryを使用せず、マネージャー経由でのDB操作を検証
    """
    def setUp(self):
        # テスト用のユーザーと書籍（在庫あり）を準備
        self.user = UserFactory(lending_period_days=14)
        self.book = BookFactory(status=1)  # Book.Status.AVAILABLE を想定

    def test_lend_success(self):
        """lend: 正常に貸出処理が行われ、書籍のステータスが更新されるか"""
        lending = Lending.objects.lend(self.book, self.user)
        
        self.assertEqual(lending.user, self.user)
        self.assertEqual(lending.book, self.book)
        self.assertEqual(lending.status, Lending.Status.LENDING)
        
        # 書籍側のステータスが LENT(2) になっているか確認
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, 2)

    def test_collect_success(self):
        """collect: 正常に返却処理が行われ、書籍が再利用可能になるか"""
        # 貸出中レコードを作成
        lending = Lending.objects.lend(self.book, self.user)
        
        # 返却実行
        returned_lending = Lending.objects.collect(lending, self.user)
        
        self.assertEqual(returned_lending.status, Lending.Status.RETURNED)
        self.assertEqual(returned_lending.return_date, timezone.now().date())
        
        # 書籍側のステータスが AVAILABLE(1) に戻っているか確認
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, 1)

    def test_renew_success(self):
        """renew: 貸出期間が正常に延長されるか"""
        lending = Lending.objects.lend(self.book, self.user)
        initial_due_date = lending.due_date
        
        # 14日間延長
        renewed_lending = Lending.objects.renew(lending, self.user, days=14)
        
        self.assertEqual(
            renewed_lending.due_date, 
            initial_due_date + timezone.timedelta(days=14)
        )

    def test_lend_fail_unavailable_book(self):
        """異常系: 既に貸出中(status=2)の書籍を貸し出そうとした際にエラーが出るか"""
        self.book.status = 2
        self.book.save()
        
        # Lending.clean() でのバリデーションを想定
        with self.assertRaises(ValidationError):
            Lending.objects.lend(self.book, self.user)


class LendingModelTest(TestCase):
    """
    Lendingモデルの定義、プロパティ、バリデーションをテストするクラス
    """
    # ① 共通テスト項目
    def test_create_success(self):
        """Factoryでエラーなくインスタンスが作成・保存できるか"""
        lending = LendingFactory()
        self.assertTrue(Lending.objects.filter(pk=lending.pk).exists())

    def test_str_representation(self):
        """__str__ が期待通りの値を返すか（TransactionBase依存の場合はその挙動を確認）"""
        lending = LendingFactory()
        # 現状の定義ではデフォルトの "Lending object (pk)"
        self.assertIn("Lending object", str(lending))

    def test_required_fields(self):
        """必須項目（due_date等）を欠いた際の ValidationError 確認"""
        lending = LendingFactory()
        lending.due_date = None
        with self.assertRaises(ValidationError):
            lending.full_clean()

    def test_unique_constraint(self):
        """モデルレベルでの一意制約があれば記述（現状はなし）"""
        pass

    def test_max_length_constraint(self):
        """remarksフィールドなどの長さ制限があれば記述（現状はTextFieldのため対象外）"""
        pass

    # ② 個別テスト項目
    def test_is_overdue_logic(self):
        """is_overdue: 正常系 → 異常系 → 境界値の順で検証"""
        # 正常系: 期限内の貸出
        lending_ok = LendingFactory(
            due_date=timezone.now().date() + timezone.timedelta(days=1),
            status=Lending.Status.LENDING
        )
        self.assertFalse(lending_ok.is_overdue())

        # 異常系: 期限を過ぎているが「返却済み」の場合は延滞ではない
        lending_returned = LendingFactory(
            due_date=timezone.now().date() - timezone.timedelta(days=1),
            status=Lending.Status.RETURNED
        )
        self.assertFalse(lending_returned.is_overdue())

        # 境界値: 期限当日
        lending_today = LendingFactory(
            due_date=timezone.now().date(),
            status=Lending.Status.LENDING
        )
        self.assertFalse(lending_today.is_overdue())

        # 境界値: 期限昨日（延滞発生）
        lending_overdue = LendingFactory(
            due_date=timezone.now().date() - timezone.timedelta(days=1),
            status=Lending.Status.LENDING
        )
        self.assertTrue(lending_overdue.is_overdue())

    def test_clean_method_lending_limit(self):
        """clean: ユーザーの貸出上限チェックの検証"""
        user = UserFactory()
        # 既に上限まで借りている状態を想定
        user.can_lend = lambda: False # モック的な挙動
        
        # buildでインスタンス作成（保存前）
        lending = LendingFactory.build(user=user)
        
        # models.py の clean() 内の user.can_lend() チェックを確認
        with self.assertRaisesRegex(ValidationError, "貸出上限"):
            lending.clean()
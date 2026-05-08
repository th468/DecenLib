import datetime
import factory
from factory.django import DjangoModelFactory
from django.test import TestCase
from django.db import models, IntegrityError, connection
from core.models.base import BaseModel
from core.models.mixins import RenameuniqueFieldsMixin
# --- 1. テスト用の具象モデル ---
# このファイル内だけで完結させる
class TestModel(BaseModel):
    code = models.CharField("コード", max_length=100, unique=True)
    title = models.CharField("タイトル", max_length=100, null=True, blank=True)
    

    class Meta:
        app_label = 'core'

    
class TestuniqueModel(BaseModel, RenameuniqueFieldsMixin):
    code = models.CharField("コード", max_length=100, unique=True)
    title = models.CharField("タイトル", max_length=100, null=True, blank=True)
    
    delete_unique_fields = ['code']
    class Meta:
        app_label = 'core'

# --- 2. テスト用モデルのFactory ---
# 相互インポートを防ぐため、ここに定義する
class TestModelFactory(DjangoModelFactory):
    class Meta:
        model = TestModel

    code = factory.Sequence(lambda n: f"code-{n}")
    title = factory.Faker("word", locale="ja_JP")
    is_active = True

# --- 3. テストクラス群 ---

class BaseManagerAndQuerySetTest(TestCase):
    """
    バルク操作（QuerySet単位）の論理削除ロジックをテストする
    """

    @classmethod
    def setUpClass(cls):
        # 1. 物理的なテーブルをテスト用DBに作成する
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestModel)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # 2. テスト終了後にテーブルを削除する
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(TestModel)

    def setUp(self):
        self.objs = TestModelFactory.create_batch(3)

    def test_queryset_logical_delete(self):
        """TestModel.objects.all().delete() で is_active=False に更新されるか"""
        TestModel.objects.all().delete()
        
        # デフォルトマネージャーでは取得できないため all_objects を使用
        all_data = TestModel.all_objects.all()
        self.assertEqual(all_data.count(), 3)
        for obj in all_data:
            self.assertFalse(obj.is_active)

    def test_queryset_hard_delete(self):
        """hard_delete() でレコードが物理削除されるか"""
        TestModel.objects.all().hard_delete()
        self.assertEqual(TestModel.all_objects.count(), 0)

    def test_manager_active_filter(self):
        """objects.all() がデフォルトで is_active=True のみを返すか"""
        TestModelFactory(is_active=False) # 1つ論理削除済みを作成
        active_count = TestModel.objects.count()
        
        self.assertEqual(active_count, 3) # setUpで作った3つのみ

    def test_all_objects_manager(self):
        """all_objects.all() で論理削除済みも含めて全件取得できるか"""
        TestModelFactory(is_active=False)
        self.assertEqual(TestModel.all_objects.count(), 4)


class BaseModelInstanceTest(TestCase):
    """
    個別インスタンスの挙動とリネームロジックをテストする
    """
    @classmethod
    def setUpClass(cls):
        # 1. 物理的なテーブルをテスト用DBに作成する
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestModel)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # 2. テスト終了後にテーブルを削除する
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(TestModel)

    def test_instance_logical_delete(self):
        """obj.delete() で is_active=False になり、DBに残るか"""
        obj = TestModelFactory(title="削除テスト")
        obj.delete()
        
        obj.refresh_from_db()
        self.assertFalse(obj.is_active)
        self.assertTrue(TestModel.all_objects.filter(pk=obj.pk).exists())

    def test_instance_hard_delete(self):
        """obj.hard_delete() で物理削除されるか"""
        obj = TestModelFactory()
        obj.hard_delete()
        self.assertFalse(TestModel.all_objects.filter(pk=obj.pk).exists())

    

    def test_str_representation(self):
        """__str__ が期待通りの形式を返すか"""
        # title がある場合
        obj_with_title = TestModelFactory(title="テスト書誌")
        self.assertEqual(str(obj_with_title), f"[{obj_with_title.pk}] テスト書誌")
        
        # title がない場合 (fallback: クラス名)
        obj_no_title = TestModelFactory(title=None)
        self.assertEqual(str(obj_no_title), f"[{obj_no_title.pk}] TestModel")

    def test_updated_at_change(self):
        """delete()（論理削除）実行時に updated_at が更新されるか"""
        obj = TestModelFactory()
        old_updated_at = obj.updated_at
        
        # 実行
        obj.delete()
        obj.refresh_from_db()
        
        self.assertGreater(obj.updated_at, old_updated_at)

class RenameuniqueFieldsMixinTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        # 1. 物理的なテーブルをテスト用DBに作成する
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestModel)
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # 2. テスト終了後にテーブルを削除する
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(TestModel)
    def test_unique_field_rename(self):
        """
        delete_unique_fields のリネームと、同一値での再保存が可能か
        """
        original_code = "UNIQUE-001"
        obj = TestModelFactory(code=original_code)
        
        # 論理削除実行
        obj.delete()
        obj.refresh_from_db()
        
        # ① 接尾辞 _del_YYYYMMDDHHMMSS が付与されているか
        self.assertIn(f"{original_code}_del_", obj.code)
        # フォーマット確認 (例: _del_20231027123456)
        suffix_part = obj.code.split("_del_")[-1]
        self.assertEqual(len(suffix_part), 14) 

        # ② 元の値と同じ値で新しいインスタンスが保存できるか（衝突回避）
        try:
            new_obj = TestModelFactory(code=original_code)
        except IntegrityError:
            self.fail("論理削除後のリネームが不十分なため、一意制約の衝突が発生しました。")
        
        self.assertEqual(new_obj.code, original_code)
    def test_perform_rename(self):
        class TestModel(BaseModel, RenameuniqueFieldsMixin):
            delete_unique_fields = ["code"]
        
        obj = TestModelFactory(code="UNIQUE-001")
        obj.delete()
        
        self.assertTrue(obj.code.endswith("_del_"))
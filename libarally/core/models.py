from django.db import models


class BaseQuerySet(models.QuerySet):
    """プロジェクト共通のクエリ操作"""
    def delete(self):
        """バルク削除 (queryset.delete()) を論理削除に書き換え"""
        return super().update(is_active=False)

    def hard_delete(self):
        """物理削除を行いたい場合に使用"""
        return super().delete()

    def active(self):
        """有効なデータのみ"""
        return self.filter(is_active=True)

class BaseManager(models.Manager):
    """通常使用するマネージャー"""
    def get_queryset(self):
        # デフォルトで is_active=True のものを返す
        return BaseQuerySet(self.model, using=self._db).filter(is_active=True)

    def active(self):
        return self.get_queryset()



class BaseModel(models.Model):
    is_active = models.BooleanField("有効フラグ", default=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    remarks = models.TextField("備考", null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        # 名前かタイトルがあればそれを表示、なければIDを表示
        name = getattr(self, 'title', getattr(self, 'name', ''))
        return f"[{self.pk}] {name}" if name else f"[{self.pk}] {self.__class__.__name__}"

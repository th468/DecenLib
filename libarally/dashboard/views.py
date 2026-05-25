from django.views.generic import TemplateView
from books.models import Biblio

class DashboardIndexView(TemplateView):
    """
    サイトトップ / ダッシュボード
    ログイン状況に応じて「紹介ページ」と「ユーザー専用ダッシュボード」を出し分ける。
    """
    
    def get_template_names(self):
        # ログイン状態によって使用するテンプレートを動的に切り替え
        if self.request.user.is_authenticated:
            return ["dashboard/index.html"]
        return ["dashboard/landing.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # ログイン済みの場合のみ、ダッシュボード用のデータを取得
        if self.request.user.is_authenticated:
            # ユーザー共通の情報（新着本など）を取得
            context['recent_biblios'] = Biblio.objects.all().order_by('-created_at')[:5]
        
        return context

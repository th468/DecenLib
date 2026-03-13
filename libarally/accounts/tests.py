from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

# カスタムユーザーモデルに対応
User = get_user_model()

class LoginTest(TestCase):
    
    def setUp(self):
        """テスト実行前のデータ準備"""
        self.password = "test_password123"
        self.user = User.objects.create_user(
            email="test@example.com",
            em_num="12345",
            password=self.password
        )
        self.login_url = reverse('accounts:login')  # urls.pyでname='login'としたもの

    def test_login_success(self):
        """正しい資格情報でログインできるか（正常系）"""
        # 1. ログイン画面にPOSTリクエストを送る
        response = self.client.post(self.login_url, {
            'email': self.user.email,
            'password': self.password
        })
        
        # 2. 成功後、期待したページ（例: ホーム）にリダイレクトされるか
        # 実際のリダイレクト先に合わせて reverse('home') などに変えてください
        self.assertRedirects(response, reverse('accounts:index'))
        
        # 3. セッションにユーザーが正しく保持されているか
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_failure_wrong_password(self):
        """間違ったパスワードでログインに失敗するか（異常系）"""
        response = self.client.post(self.login_url, {
            'email': self.user.email,
            'password': 'wrong_password'
        })
        
        # ログインに失敗し、同じページ（200 OK）に戻ってくるか
        self.assertEqual(response.status_code, 200)
        # エラーメッセージが画面に表示されているか
        self.assertContains(response, "ログインに失敗しました")
        # セッションにユーザーが入っていないことを確認
        self.assertNotIn('_auth_user_id', self.client.session)
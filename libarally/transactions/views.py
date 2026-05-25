from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from books.models import Biblio, Book
from .models import Lending, Reservation


# 貸出実行
class LendActionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        try:
            Lending.objects.lend(book, request.user)
            # 成功フラグをセッションにセット（詳細画面でのモーダル発火用）
            request.session['reveal_location'] = True
            messages.success(request, f"「{book.biblio.title}」の貸出手続きが完了しました。")
        except ValidationError as e:
            messages.error(request, e.message)
        
        return redirect(reverse('books:bookdetail', kwargs={'pk': pk}))


# 予約実行
class ReserveActionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # 詳細画面のBookIDから予約を行う
        book = get_object_or_404(Book, pk=pk)
        try:
            Reservation.objects.create_reservation(request.user, book.biblio)
            request.session['reveal_location'] = True
            messages.success(request, f"「{book.biblio.title}」を予約しました。")
        except ValidationError as e:
            messages.error(request, e.message)
        
        return redirect(reverse('books:bookdetail', kwargs={'pk': pk}))


# 返却実行
class CollectActionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        lending = get_object_or_404(Lending, pk=pk)
        try:
            Lending.objects.collect(lending, request.user)
            messages.success(request, "返却が完了しました。")
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect('dashboard:index')


# 延長実行
class RenewActionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        lending = get_object_or_404(Lending, pk=pk)
        try:
            Lending.objects.renew(lending, request.user)
            messages.success(request, "貸出期間を延長しました。")
        except ValidationError as e:
            messages.error(request, e.message)
        return redirect('dashboard:index')

from django.shortcuts import render
from django.views.generic import ListView,DetailView
from django.db.models import Q
from .models import Book

def index(request):
    return render(request, "books/index.html")


#書籍一覧
class BookListView(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    ordering = ["-created_at"]
    paginate_by = 10
#検索機能
    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return Book.objects.filter(
                Q(biblio__title__icontains=query) |
                Q(biblio__author__icontains=query)|
                Q(biblio__isbn__exact=query)
            )
        else:
            return Book.objects.all()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
# 検索条件に応じてタイトルを変更
        query = self.request.GET.get("q")
        if query:
            context["page_title"] = f"[{query}]の検索結果[{self.object_list.count()}件]"
        else:
            context["page_title"] = "蔵書一覧"
        
        return context



#詳細画面
class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"


from django.urls import path
from . import views

app_name = "books"


urlpatterns = [
    path("",views.index, name="index"),
    path("booklist/", views.BookListView.as_view(), name="booklist"),
    path("bookdetail/<int:pk>/", views.BookDetailView.as_view(), name="bookdetail"),

]
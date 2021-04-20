from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = "App"

urlpatterns = [
    path("", views.login, name="login"),
    path("register", views.register, name="register"),
    path("login", views.login, name="login"),
    path("index", views.index, name="index"),
    path("search-books", views.search_books, name="search_books"),
    path("detail/<slug>", views.detail, name="detail"),
    path("add-book", views.add_book, name="add_book"),


]

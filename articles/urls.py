from django.urls import path
from . import views

app_name="articles"
urlpatterns = [
    path("articles_main/", views.articles_main, name="articles_main"),
    path("create", views.create, name="create"),
    path("<int:article_pk>/articles_detail", views.articles_detail, name="articles_detail"),
    path("<int:article_pk>/articles_delete", views.articles_delete, name="articles_delete"),
    path("<int:article_pk>/articles_update", views.articles_update, name="articles_update"),
    path("comment/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),
    path("toggle_like/", views.toggle_like, name="toggle_like"),
    path("toggle_dislike/", views.toggle_dislike, name="toggle_dislike"),
]


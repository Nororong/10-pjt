from django.urls import path
from . import views

app_name = 'movies'
urlpatterns = [
    path('', views.index, name='index'),
    path('movie_list/', views.movie_list, name='movie_list'),
    path('<int:movie_pk>/likes/', views.likes, name='likes'),
    # path('create/', views.create, name='create'),
    # path('<int:pk>/delete/', views.delete, name='delete'),
    # path('<int:pk>/update/', views.update, name='update'),
]
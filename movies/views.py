from django.shortcuts import render
from movies.models import Movie
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        favorite_directors = request.user.favorite_directors.all()
        favorite_genres = request.user.favorite_genres.all()
        favorite_awards = request.user.favorite_awards.all()
        
        context = {
            'favorite_directors': favorite_directors,
            'favorite_genres': favorite_genres,
            'favorite_awards': favorite_awards,
        }
        return render(request, 'movies/index.html', context)
    return render(request, 'movies/index.html')

# 영화 전체 리스트 페이지
# def movie_list(request):
#     movies = Movie.objects.all()  # 데이터베이스에서 모든 영화 가져오기

#     liked_movie = []
#     if request.user.is_authenticated:
#         liked_movie = request.user.like_movies.values_list('id', flat=True)
    
#     context = {
#         'movies': movies,
#         'liked_movie': list(liked_movie)
#     }
#     return render(request, 'movies/movie_list.html', context)

def movie_list(request):
    movies = Movie.objects.all()

    liked_movie_ids = []
    if request.user.is_authenticated:
        liked_movie_ids = request.user.like_movies.values_list('id', flat=True)
    
    context = {
        'movies': movies,
        'liked_movie_ids': list(liked_movie_ids),
    }
    return render(request, 'movies/movie_list.html', context)


@login_required
def likes(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)

    if request.user in movie.like_users.all():
        movie.like_users.remove(request.user)
        is_liked = False
    else:
        movie.like_users.add(request.user)
        is_liked = True
    
    context = {
        'is_liked': is_liked
    }
    return JsonResponse(context)
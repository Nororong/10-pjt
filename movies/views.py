from django.shortcuts import render, redirect
from movies.models import Movie, MovieComment, Genre
from .forms import MovieCommentForm, CityForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings
from django.urls import reverse
from articles.models import Article, Comment
import json
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
    # 모든 영화와 관련된 장르를 미리 가져온다 -> 쿼리 최적화
    movies = Movie.objects.all().prefetch_related('genres')
    # 모든 장르를 가져온다
    genres = Genre.objects.all()

    # 사용자가 좋아요를 누른 영화 ID 목록
    liked_movie_ids = []
    if request.user.is_authenticated:
        # 로그인 한 사용자일 경우, 좋아요를 누른 영화의 ID를 가져온다
        liked_movie_ids = request.user.like_movies.values_list('id', flat=True)
    
    context = {
        'movies': movies,
        'liked_movie_ids': list(liked_movie_ids),
        'genres': genres,
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


def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    
    # QuerySet에서 ID만 추출하고 TMDB_GENRES를 통해 이름 매핑
    genre_ids = movie.genres.values_list('tmdb_id', flat=True)
    genres = Genre.objects.filter(tmdb_id__in=genre_ids).values_list('name', flat=True)

    # 나머지 데이터
    movie_comment_form = MovieCommentForm()
    movie_comments = movie.moviecomment_set.all()
    actors = movie.actors.all()

    print(f"Genre IDs: {list(genre_ids)}")
    print(f"Genres: {list(genres)}")
    
    context = {
        'movie': movie,
        'genres': genres, 
        'actors': actors,
        'movie_comment_form': movie_comment_form,
        'movie_comments': movie_comments,
    }
    return render(request, 'movies/movie_detail.html', context)

@login_required
def movie_comments_create(request, movie_comment_pk):
    movie = get_object_or_404(Movie, pk=movie_comment_pk)
    movie_comment_form = MovieCommentForm(request.POST)

    if movie_comment_form.is_valid():
        movie_comment = movie_comment_form.save(commit=False)
        movie_comment.movie = movie
        movie_comment.user = request.user
        movie_comment.save()
        return redirect('movies:movie_detail', movie.pk)
    
    context = {
        'movie': movie,
        'movie_comment_form': movie_comment_form,
    }
    return render(request, 'movies/movie_detail.html', context)

@login_required
def movie_comments_delete(request, movie_pk, movie_comment_pk):
    movie_comment = MovieComment.objects.get(pk=movie_comment_pk)
    movie = Movie.objects.get(pk=movie_pk)

    if request.user == movie_comment.user:
        movie_comment.delete()
    return redirect('movies:movie_detail', movie.pk)

# 날씨정보를 얻기 위한 view함수
from django.shortcuts import render
import requests
from django.conf import settings
from .forms import CityForm  # 이 부분에서 CityForm을 import한다고 가정

def get_weather_data(city):
    api_key = settings.OPENWEATHERMAP_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    return None


from movies.models import Movie  # Movie 모델을 임포트

@login_required
def weather_view(request, city):
    weather_data = get_weather_data(city)
    context = {}

    if weather_data:
        weather_condition = weather_data['weather'][0]['main']
        description = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']

        user_genres = request.user.favorite_genres.all()

        # 날씨와 선호 장르를 기반으로 영화 필터링
        if user_genres.exists():
            movies = Movie.objects.filter(genres__in=user_genres, weather__icontains=weather_condition).distinct()
        else:
            movies = Movie.objects.filter(weather__icontains=weather_condition).distinct()

        movies_with_temp = []
        for movie in movies:
            movies_with_temp.append({
                'id': movie.id,
                'title': movie.title,
                'poster_path': movie.poster_path,
                'genres': movie.genres.all(),
                'recommended_temperature': movie.recommended_temperature
            })

        context = {
            'city': city,
            'weather_condition': weather_condition,
            'description': description,
            'temperature': temperature,
            'humidity': humidity,
            'movies': movies_with_temp,
        }
    else:
        context['error'] = '날씨를 불러올 수 없어요. 올바른 도시명을 다시 입력해주세요!'

    return render(request, 'movies/weather.html', context)


@login_required
def weather_input(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            return redirect(reverse('movies:weather', args=[city]))
    else:
        form = CityForm()
    context = {
        'form' : form,
    }
    
    return render(request, 'movies/weather_input.html', context)

def movie_record(request):
    # 1. 찜한 영화 목록
    liked_movies = request.user.like_movies.all()

    # 2. 작성한 영화 댓글
    movie_comments = MovieComment.objects.filter(user=request.user)

    # 3. 작성한 커뮤니티 글
    user_articles = Article.objects.filter(author=request.user)

    # 4. 작성한 커뮤니티 댓글
    user_comments = Comment.objects.filter(author=request.user)

    context = {
        'liked_movies': liked_movies,
        'movie_comments': movie_comments,
        'user_articles': user_articles,
        'user_comments': user_comments,
    }
    return render(request, 'movies/movie_record.html', context)


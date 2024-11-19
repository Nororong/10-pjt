from django.shortcuts import render

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

# def movie_()

from django import forms
from .models import MovieComment

class MovieCommentForm(forms.ModelForm):
    class Meta:
        model = MovieComment
        fields = ('content',)

class CityForm(forms.Form):
    city = forms.CharField(max_length=50, label="City Name")
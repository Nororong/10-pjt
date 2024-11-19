from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django import forms
from .models import Award, Director, Genre

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username', 'password1', 'password2', 
            'first_name', 'last_name', 'email', 
            'birth_date', 'gender'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CustomUserChangeForm(UserChangeForm):
    password = None
    favorite_directors = forms.ModelMultipleChoiceField(
        queryset=Director.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    favorite_genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    favorite_awards = forms.ModelMultipleChoiceField(
        queryset=Award.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date', 'gender', 'favorite_directors', 'favorite_genres', 'favorite_awards')


class PreferenceForm(forms.ModelForm):
    favorite_directors = forms.ModelMultipleChoiceField(
        queryset=Director.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    favorite_genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    favorite_awards = forms.ModelMultipleChoiceField(
        queryset=Award.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = User
        fields = ['favorite_directors', 'favorite_genres', 'favorite_awards']

    def clean(self):
        cleaned_data = super().clean()
        for field in ['favorite_directors', 'favorite_genres', 'favorite_awards']:
            if len(cleaned_data.get(field, [])) > 3:
                raise forms.ValidationError(f"{field}는 최대 3개까지만 선택할 수 있습니다.")
        return cleaned_data
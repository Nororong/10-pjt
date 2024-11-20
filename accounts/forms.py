from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django import forms
from .models import Award, Director, Genre

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="생년월일")

    class Meta:
        model = User
        fields = [
            'username', 'password1', 'password2', 
            'first_name', 'last_name', 'email', 
            'birth_date'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'username': '아이디',
            'password1': '비밀번호',
            'password2': '비밀번호 확인',
            'first_name': '이름',
            'last_name': '성',
            'email': '이메일',
            'birth_date': '생년월일',
        }

    # 비밀번호 관련 기본 유효성 검사 메시지 없애기
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 비밀번호 필드 메시지를 빈 메시지로 설정
        self.fields['password1'].error_messages = {
            'required': '', 
            'too_common': '',
            'too_similar': '',
            'too_short': '',
            'numeric': ''
        }
        self.fields['password2'].error_messages = {
            'required': '', 
            'password_mismatch': ''
        }

    # 다른 필드들에 대해서도 필요시 메시지 제거 가능
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("비밀번호 확인이 일치하지 않습니다.")
        return password2
        

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
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date', 'favorite_directors', 'favorite_genres', 'favorite_awards')


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
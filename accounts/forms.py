from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django import forms
from .models import Award, Director, Genre
from django.contrib.auth.forms import PasswordChangeForm
User = get_user_model()
from django.utils.translation import gettext_lazy
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
    
class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 각 필드의 위젯에 클래스 추가
        self.fields['old_password'].widget.attrs.update({
            'class': 'password-change-input'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'password-change-input'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'password-change-input'
        })
        
        self.error_messages = {
            'password_incorrect': '기존 비밀번호가 일치하지 않습니다.',
            'password_mismatch': '두 비밀번호가 일치하지 않습니다.',
            'password_too_similar': '비밀번호가 사용자 이름과 너무 유사합니다.',
            'password_too_short': '비밀번호가 너무 짧습니다. 최소 8자 이상이어야 합니다.',
            'password_too_common': '비밀번호가 너무 일반적입니다.',
            'password_entirely_numeric': '비밀번호는 숫자로만 이루어질 수 없습니다.',
        }

        # 각 필드의 help_text 제거 (선택사항)
        self.fields['new_password1'].help_text = ''
        self.fields['new_password2'].help_text = ''

    def clean_new_password2(self):
        old_password = self.cleaned_data.get('old_password')
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')

        # 기본 유효성 검사 수행
        new_password2 = super().clean_new_password2()

        # 이전 비밀번호와 새 비밀번호가 같은지 확인
        if old_password and new_password1 and old_password == new_password1:
            raise ValidationError(
                _("새 비밀번호는 이전 비밀번호와 같을 수 없습니다."),
                code='password_unchanged'
            )

        return new_password2

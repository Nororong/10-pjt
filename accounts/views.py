from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserChangeForm, PreferenceForm, CustomPasswordChangeForm
from .forms import PreferenceForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .models import Genre

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user) 
            return redirect('accounts:preference')
    else:
        form = CustomUserCreationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/signup.html', context)

def login(request): 
    if request.user.is_authenticated:
        return redirect('movies:index')

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('movies:index')
    else:
        form = AuthenticationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)

def preference(request):
    if request.method == 'POST':
        form = PreferenceForm(request.POST, instance=request.user)
        if form.is_valid():
            # 먼저 사용자 정보 저장
            user = form.save(commit=False)  # commit=False로 먼저 저장
            user.save()  # 사용자 객체 저장

            # 기존 선호 장르 초기화
            user.favorite_genres.clear()

            # 새로 선택된 장르 추가 (장르가 존재하는지 확인)
            for genre in form.cleaned_data['favorite_genres']:
                if Genre.objects.filter(id=genre.id).exists():  # 장르가 존재하는지 확인
                    user.favorite_genres.add(genre.pk)  # genre의 pk 값을 사용
                else:
                    messages.error(request, f"선택한 장르 '{genre}'가 존재하지 않습니다.")
                    return redirect('accounts:preference')

            messages.success(request, '선호도가 성공적으로 저장되었습니다.')
            return redirect('movies:index')
    else:
        form = PreferenceForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'accounts/preference.html', context)

@login_required
def logout(request):
    auth_logout(request)
    return redirect('movies:index')

@login_required
def delete(request):
    user= request.user
    logout(request)
    user.delete()
    return redirect('movies:index')

@login_required
def update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('movies:index')
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'accounts/update.html', context)

def set_preferences(request):
    if request.method == 'POST':
        form = PreferenceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('preferences:show_preferences')  # 선호도 정보 페이지로 리다이렉트
    else:
        form = PreferenceForm(instance=request.user)
    context ={
        'form' : form,
    }
    return render(request, 'preferences/set_preferences.html', context)

def show_preferences(request):
    user = request.user
    context = {
        'favorite_directors': user.favorite_directors.all(),
        'favorite_genres': user.favorite_genres.all(),
        'favorite_awards': user.favorite_awards.all(),
    }
    return render(request, 'preferences/show_preferences.html', context)

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change.html'
    
    def get_success_url(self):
        # movies 페이지로 리다이렉트
        return reverse_lazy('movies:index')  # movies 앱의 index URL name 사용
    
    def form_valid(self, form):
        # 부모 메서드 호출
        response = super().form_valid(form)
        
        # 선택적으로 성공 메시지 추가 가능
        from django.contrib import messages
        messages.success(self.request, '비밀번호가 성공적으로 변경되었습니다.')
        
        return response
    
@login_required
def password_change(request, user_pk):
    User = get_user_model()
    user = get_object_or_404(User, pk=user_pk)
    if request.user != user:
        return redirect('movies:index') 
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('movies:index')
    else:
        form = CustomPasswordChangeForm(user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/password_change.html', context)


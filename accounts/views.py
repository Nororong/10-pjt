from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserChangeForm, PreferenceForm
from .forms import PreferenceForm
from django.contrib.auth import login  # Make sure to import login

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

@login_required
def preference(request):
    if request.method == 'POST':
        form = PreferenceForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '선호도가 성공적으로 저장되었습니다.')
            return redirect('movies:index')
        else:
            messages.error(request, '선호도 저장에 실패했습니다. 입력을 확인해주세요.')
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
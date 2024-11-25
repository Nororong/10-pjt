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
from .models import Genre, User
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
import requests
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from smtplib import SMTPException
from user_agent import generate_user_agent
# from .utils import send_id_email
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
            user = form.save(commit=False)
            user.save()
            
            # ManyToManyField 저장
            form.save_m2m()  # 이 부분이 중요합니다!
            
            messages.success(request, '선호하는 장르가 성공적으로 저장되었습니다.')
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
    user = request.user
    logout(request)
    user.delete()

    messages.success(request, "회원탈퇴가 이루어졌습니다.")  # First argument should be request
    return redirect('movies:index')

import logging

logger = logging.getLogger(__name__)

@login_required
def update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            # ManyToMany 관계 업데이트
            favorite_genres = form.cleaned_data['favorite_genres']
            request.user.favorite_genres.set(favorite_genres)
            
            messages.success(request, "성공적으로 수정되었습니다!")
            return redirect('movies:index')
        else:
            messages.error(request, "수정에 실패했습니다. 다시 시도해주세요.")
    else:
        form = CustomUserChangeForm(instance=request.user)
        # 초기값 설정
        form.fields['favorite_genres'].initial = request.user.favorite_genres.all()

    context = {
        'form': form
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

def mypage(request):
    return render(request, 'accounts/mypage.html')

def send_id_email(user, email):
    subject = "아이디 찾기 결과"
    body = f"안녕하세요, 요청하신 아이디는 {user.username}입니다."

    # 메일 보내는 SMTP 서버 설정
    sender_email = settings.DEFAULT_FROM_EMAIL  # 보낼 이메일 주소 (ex: 네이버 메일)
    receiver_email = email  # 받는 이메일 주소
    password = settings.EMAIL_HOST_PASSWORD  # 이메일 계정 비밀번호

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # SMTP 서버에 연결
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()  # TLS 연결 시작
            server.login(sender_email, password)  # 로그인
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)  # 이메일 전송
        return True
    except Exception as e:
        print(f"이메일 전송 실패: {e}")
        return False
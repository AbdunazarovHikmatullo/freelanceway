from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, CustomPasswordChangeForm
from .models import User
from freelancers.models import Freelancer


def register_view(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('index')


    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Если пользователь выбрал тип "фрилансер", создаем профиль фрилансера
            if user.is_freelancer:
                login(request, user)
                return redirect('create_freelancer_profile')
            # Автоматически входим пользователя после регистрации
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            
            
            return redirect('users:profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Проверяем, является ли username email-адресом
            if '@' in username:
                try:
                    user = User.objects.get(email=username)
                    username = user.username
                except User.DoesNotExist:
                    pass
            
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                
                # Перенаправляем на запрошенную страницу или на главную
                next_page = request.GET.get('next', 'index')
                return redirect(next_page)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """Выход пользователя"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('index')


@login_required(login_url='users:login')
def profile_view(request):
    """Просмотр профиля пользователя"""
    user = request.user
    
    # Проверяем, есть ли у пользователя профиль фрилансера
    freelancer_profile = None
    if user.is_freelancer:
        try:
            freelancer_profile = Freelancer.objects.get(user=user)
        except Freelancer.DoesNotExist:
            pass
    
    # Получаем статистику пользователя
    context = {
        'user': user,
        'freelancer_profile': freelancer_profile,
    }
    
    # Если пользователь - заказчик, добавляем статистику по вакансиям
    if user.is_client:
        from vacancy.models import Vacancy
        vacancies = Vacancy.objects.filter(client=user)
        open_vacancies = vacancies.filter(status='open').count()
        in_progress_vacancies = vacancies.filter(status='in_progress').count()
        completed_vacancies = vacancies.filter(status='completed').count()
        
        context.update({
            'vacancies': vacancies,
            'open_vacancies': open_vacancies,
            'in_progress_vacancies': in_progress_vacancies,
            'completed_vacancies': completed_vacancies,
        })
    
    # Если пользователь - фрилансер, добавляем статистику по заявкам
    if user.is_freelancer and freelancer_profile:
        from vacancy.models import Application
        applications = Application.objects.filter(freelancer=freelancer_profile)
        pending_applications = applications.filter(status='pending').count()
        accepted_applications = applications.filter(status='accepted').count()
        rejected_applications = applications.filter(status='rejected').count()
        
        context.update({
            'applications': applications,
            'pending_applications': pending_applications,
            'accepted_applications': accepted_applications,
            'rejected_applications': rejected_applications,
        })
    
    return render(request, 'users/profile.html', context)


@login_required(login_url='users:login')
def edit_profile_view(request):
    """Редактирование профиля пользователя"""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required(login_url='users:login')
def change_password_view(request):
    """Изменение пароля пользователя"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Обновляем сессию, чтобы пользователь не вышел из системы
            update_session_auth_hash(request, user)
            messages.success(request, 'Ваш пароль был успешно изменен!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


def public_profile_view(request, username):
    """Просмотр публичного профиля пользователя"""
    user = get_object_or_404(User, username=username)
    
    # Проверяем, есть ли у пользователя профиль фрилансера
    freelancer_profile = None
    if user.is_freelancer:
        try:
            freelancer_profile = Freelancer.objects.get(user=user)
        except Freelancer.DoesNotExist:
            pass
    
    context = {
        'profile_user': user,
        'freelancer_profile': freelancer_profile,
    }
    
    return render(request, 'users/public_profile.html', context)
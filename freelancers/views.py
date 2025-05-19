from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
from .models import Freelancer, Review
from .forms import ReviewForm
from notifications.services import NotificationService

from .models import Freelancer, Portfolio, Review, Category
from .forms import FreelancerProfileForm, PortfolioForm, ReviewForm, FreelancerFilterForm
from users.models import User


def freelancers_list(request):
    """Отображение списка фрилансеров с фильтрацией"""
    categories = Category.objects.all()
    
    # Получаем параметры фильтрации
    form = FreelancerFilterForm(request.GET)
    
    # Базовый запрос
    freelancers = Freelancer.objects.select_related('user').all()
    
    # Применяем фильтры
    if form.is_valid():
        category = form.cleaned_data.get('category')
        experience = form.cleaned_data.get('experience')
        min_rating = form.cleaned_data.get('min_rating')
        availability = form.cleaned_data.get('availability')
        skills = form.cleaned_data.get('skills')
        sort_by = form.cleaned_data.get('sort_by')
        
        if category:
            freelancers = freelancers.filter(categories=category)
        
        if experience:
            freelancers = freelancers.filter(experience=experience)
        
        if min_rating:
            freelancers = freelancers.filter(rating__gte=float(min_rating))
        
        if availability:
            freelancers = freelancers.filter(availability=availability)
        
        if skills:
            skill_terms = [term.strip() for term in skills.split(',')]
            q_objects = Q()
            for term in skill_terms:
                q_objects |= Q(skills__icontains=term)
            freelancers = freelancers.filter(q_objects)
        
        # Сортировка
        if sort_by:
            freelancers = freelancers.order_by(sort_by)
    else:
        # По умолчанию сортируем по рейтингу
        freelancers = freelancers.order_by('-rating')
    
    # Пагинация
    paginator = Paginator(freelancers, 9)  # 9 фрилансеров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'form': form,
    }
    
    return render(request, 'freelancers/freelancers_list.html', context)

@login_required
def create_freelancer_profile(request):
    """Создание профиля фрилансера"""
    # Проверяем, является ли пользователь фрилансером
    if not request.user.is_freelancer:
        messages.error(request, 'Только пользователи с типом "Фрилансер" могут создать профиль фрилансера')
        return redirect('profile')
    
    # Проверяем, есть ли уже профиль фрилансера
    try:
        freelancer = Freelancer.objects.get(user=request.user)
        messages.info(request, 'У вас уже есть профиль фрилансера')
        return redirect('edit_freelancer_profile')
    except Freelancer.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = FreelancerProfileForm(request.POST)
        if form.is_valid():
            freelancer = form.save(commit=False)
            freelancer.user = request.user
            freelancer.save()
            
            # Сохраняем категории (ManyToMany)
            form.save_m2m()
            
            messages.success(request, 'Профиль фрилансера успешно создан!')
            return redirect('users:profile', username=request.user.username)
    else:
        form = FreelancerProfileForm()
    
    return render(request, 'freelancers/freelancer_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
def edit_freelancer_profile(request):
    """Редактирование профиля фрилансера"""
    # Получаем профиль фрилансера
    try:
        freelancer = Freelancer.objects.get(user=request.user)
    except Freelancer.DoesNotExist:
        messages.error(request, 'У вас нет профиля фрилансера')
        return redirect('create_freelancer_profile')
    
    if request.method == 'POST':
        form = FreelancerProfileForm(request.POST, instance=freelancer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль фрилансера успешно обновлен!')
            return redirect('freelancer_detail', username=request.user.username)
    else:
        form = FreelancerProfileForm(instance=freelancer)
    
    return render(request, 'freelancers/freelancer_form.html', {
        'form': form,
        'freelancer': freelancer,
        'is_edit': True,
    })


@login_required
def add_review(request, freelancer_id):
    """Добавление отзыва о фрилансере"""
    freelancer = get_object_or_404(Freelancer, id=freelancer_id)
    
    # Проверяем, оставлял ли пользователь уже отзыв
    if Review.objects.filter(freelancer=freelancer, author=request.user).exists():
        messages.error(request, 'Вы уже оставили отзыв для этого фрилансера.')
        return redirect('freelancer_detail', username=freelancer.user.username)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.freelancer = freelancer
            review.author = request.user
            review.save()
            
            # Обновляем рейтинг фрилансера
            avg_rating = Review.objects.filter(freelancer=freelancer).aggregate(Avg('rating'))['rating__avg']
            freelancer.rating = avg_rating
            freelancer.reviews_count = Review.objects.filter(freelancer=freelancer).count()
            freelancer.save()
            
            # Отправляем уведомление фрилансеру
            NotificationService.create_notification(
                recipient=freelancer.user,
                notification_type_code='new_review',
                title='Новый отзыв о вас',
                message=f'Пользователь {request.user.get_full_name()} оставил отзыв о вашей работе с оценкой {review.rating}/5.',
                related_object=review,
                action_url=reverse('freelancer_detail', kwargs={'username': freelancer.user.username}),
                level='info'
            )
            
            messages.success(request, 'Ваш отзыв успешно добавлен!')
            return redirect('freelancer_detail', username=freelancer.user.username)
    else:
        form = ReviewForm()
    
    return render(request, 'freelancers/review_form.html', {'form': form, 'freelancer': freelancer})


@login_required
def add_portfolio_item(request):
    """Добавление элемента портфолио"""
    # Получаем профиль фрилансера
    try:
        freelancer = Freelancer.objects.get(user=request.user)
    except Freelancer.DoesNotExist:
        messages.error(request, 'У вас нет профиля фрилансера')
        return redirect('create_freelancer_profile')
    
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            portfolio_item = form.save(commit=False)
            portfolio_item.freelancer = freelancer
            portfolio_item.save()
            messages.success(request, 'Проект успешно добавлен в портфолио!')
            return redirect('users:profile')
    else:
        form = PortfolioForm()
    
    return render(request, 'freelancers/portfolio_form.html', {
        'form': form,
    })


@login_required
def edit_portfolio_item(request, item_id):
    """Редактирование элемента портфолио"""
    portfolio_item = get_object_or_404(Portfolio, id=item_id, freelancer__user=request.user)
    
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES, instance=portfolio_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Проект успешно обновлен!')
            return redirect('users:profile', username=request.user.username)
    else:
        form = PortfolioForm(instance=portfolio_item)
    
    return render(request, 'freelancers/portfolio_form.html', {
        'form': form,
        'portfolio_item': portfolio_item,
        'is_edit': True,
    })


@login_required
def delete_portfolio_item(request, item_id):
    """Удаление элемента портфолио"""
    portfolio_item = get_object_or_404(Portfolio, id=item_id, freelancer__user=request.user)
    
    if request.method == 'POST':
        portfolio_item.delete()
        messages.success(request, 'Проект успешно удален из портфолио!')
        return redirect('freelancer_detail', username=request.user.username)
    
    return render(request, 'freelancers/portfolio_confirm_delete.html', {
        'portfolio_item': portfolio_item,
    })


@login_required
def delete_review(request, review_id):
    """Удаление отзыва"""
    review = get_object_or_404(Review, id=review_id, author=request.user)
    freelancer = review.freelancer
    
    if request.method == 'POST':
        review.delete()
        
        # Обновляем рейтинг фрилансера
        reviews = Review.objects.filter(freelancer=freelancer)
        if reviews.exists():
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            freelancer.rating = avg_rating
        else:
            freelancer.rating = 0
        
        freelancer.reviews_count = reviews.count()
        freelancer.save()
        
        messages.success(request, 'Отзыв успешно удален!')
        return redirect('freelancer_detail', username=freelancer.user.username)
    
    return render(request, 'freelancers/review_confirm_delete.html', {
        'review': review,
    })


def featured_freelancers(request):
    """API для получения рекомендуемых фрилансеров"""
    freelancers = Freelancer.objects.filter(is_featured=True).order_by('-rating')[:5]
    
    data = []
    for freelancer in freelancers:
        data.append({
            'id': freelancer.id,
            'username': freelancer.user.username,
            'name': freelancer.user.get_full_name(),
            'avatar': freelancer.user.get_avatar_url(),
            'headline': freelancer.headline,
            'rating': float(freelancer.rating),
            'hourly_rate': float(freelancer.hourly_rate),
            'url': reverse('freelancer_detail', args=[freelancer.user.username]),
        })
    
    return JsonResponse({'freelancers': data})
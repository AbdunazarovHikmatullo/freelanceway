from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Q, Count, Prefetch
from django.views.decorators.cache import cache_page

from .models import Vacancy, Category, Application
from .forms import VacancyFilterForm, VacancyForm, ApplicationForm
from utils import paginate_queryset, cache_result, invalidate_cache_pattern

# Кешируем страницу списка вакансий на 5 минут
@cache_page(60 * 5)
def vacancies_list(request):
    """Список всех вакансий с фильтрацией"""
    # Получаем параметры фильтрации из запроса
    form = VacancyFilterForm(request.GET)
    
    # Базовый QuerySet с оптимизацией запросов
    queryset = Vacancy.objects.select_related('category', 'client').prefetch_related(
        Prefetch('applications', queryset=Application.objects.filter(status='pending'), to_attr='pending_applications')
    ).annotate(
        applications_count=Count('applications')
    ).filter(status='open')
    
    # Применяем фильтры, если форма валидна
    if form.is_valid():
        data = form.cleaned_data
        
        # Фильтр по категории
        if data.get('category'):
            queryset = queryset.filter(category__slug=data['category'])
        
        # Фильтр по бюджету
        if data.get('budget_min'):
            queryset = queryset.filter(budget_max__gte=data['budget_min'])
        if data.get('budget_max'):
            queryset = queryset.filter(budget_min__lte=data['budget_max'])
        
        # Поиск по ключевым словам
        if data.get('q'):
            query = data['q']
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(required_skills__icontains=query)
            )
        
        # Сортировка
        sort_by = request.GET.get('sort', 'created_at')
        if sort_by == 'budget_max':
            queryset = queryset.order_by('-budget_max')
        elif sort_by == 'budget_min':
            queryset = queryset.order_by('-budget_min')
        else:
            queryset = queryset.order_by('-created_at')
    else:
        # По умолчанию сортируем по дате создания
        queryset = queryset.order_by('-created_at')
    
    # Пагинация с кешированием
    page_obj = paginate_queryset(
        request, 
        queryset, 
        cache_key_prefix='vacancies_list',
        cache_timeout=300  # 5 минут
    )
    
    # Получаем категории для фильтра
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'form': form,
        'search_query': request.GET.get('q', ''),
        'selected_category': request.GET.get('category', ''),
        'budget_min': request.GET.get('budget_min', ''),
        'budget_max': request.GET.get('budget_max', ''),
        'sort_by': request.GET.get('sort', 'created_at'),
    }
    
    return render(request, 'vacancy/vacancies_list.html', context)

@cache_result(timeout=3600, prefix='vacancy_detail')
def get_vacancy_detail_data(vacancy_id):
    """Получение данных для детальной страницы вакансии с кешированием"""
    vacancy = get_object_or_404(
        Vacancy.objects.select_related('category', 'client').prefetch_related(
            Prefetch('applications', queryset=Application.objects.filter(status='pending'), to_attr='pending_applications')
        ),
        id=vacancy_id
    )
    
    # Получаем похожие вакансии
    similar_vacancies = Vacancy.objects.filter(
        category=vacancy.category,
        status='open'
    ).exclude(id=vacancy.id).order_by('-created_at')[:3]
    
    return {
        'vacancy': vacancy,
        'similar_vacancies': similar_vacancies,
    }

def vacancy_detail(request, vacancy_id):
    """Детальная страница вакансии"""
    # Получаем данные из кеша или из базы данных
    data = get_vacancy_detail_data(vacancy_id)
    vacancy = data['vacancy']
    similar_vacancies = data['similar_vacancies']
    
    # Проверяем, есть ли у пользователя заявка на эту вакансию
    user_application = None
    if request.user.is_authenticated and request.user.is_freelancer:
        try:
            from freelancers.models import Freelancer
            freelancer = Freelancer.objects.get(user=request.user)
            user_application = Application.objects.filter(
                vacancy=vacancy,
                freelancer=freelancer
            ).first()
        except Freelancer.DoesNotExist:
            pass
    
    # Увеличиваем счетчик просмотров
    vacancy.views_count += 1
    vacancy.save(update_fields=['views_count'])
    
    context = {
        'vacancy': vacancy,
        'similar_vacancies': similar_vacancies,
        'user_application': user_application,
    }
    
    return render(request, 'vacancy/vacancy_detail.html', context)

@login_required
def create_vacancy(request):
    """Создание новой вакансии"""
    if not request.user.is_client:
        return redirect('users:profile')
    
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.client = request.user
            vacancy.save()
            
            # Инвалидируем кеш списка вакансий
            invalidate_cache_pattern('vacancies_list*')
            
            return redirect('vacancy:vacancy_detail', vacancy_id=vacancy.id)
    else:
        form = VacancyForm()
    
    context = {
        'form': form,
        'is_edit': False,
    }
    
    return render(request, 'vacancy/vacancy_form.html', context)

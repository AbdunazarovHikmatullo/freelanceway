from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Vacancy, Category, Application
from .forms import VacancyForm, ApplicationForm
from freelancers.models import Freelancer
from notifications.services import NotificationService
from django.urls import reverse

def vacancies_list(request):
    """Отображение списка всех вакансий с фильтрацией"""
    categories = Category.objects.all()
    
    # Получаем параметры фильтрации
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    budget_min = request.GET.get('budget_min')
    budget_max = request.GET.get('budget_max')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Базовый запрос
    vacancies = Vacancy.objects.filter(status='open')
    
    # Применяем фильтры
    if category_slug:
        vacancies = vacancies.filter(category__slug=category_slug)
    
    if search_query:
        vacancies = vacancies.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(required_skills__icontains=search_query)
        )
    
    if budget_min:
        vacancies = vacancies.filter(budget_min__gte=budget_min)
    
    if budget_max:
        vacancies = vacancies.filter(budget_max__lte=budget_max)
    
    # Сортировка
    if sort_by == 'budget_max':
        vacancies = vacancies.order_by('-budget_max')
    elif sort_by == 'budget_min':
        vacancies = vacancies.order_by('budget_min')
    elif sort_by == 'created_at':
        vacancies = vacancies.order_by('-created_at')
    
    # Пагинация
    paginator = Paginator(vacancies, 9)  # 9 вакансий на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
        'budget_min': budget_min,
        'budget_max': budget_max,
        'sort_by': sort_by,
    }
    
    return render(request, 'vacancy/vacancies_list.html', context)


def vacancy_detail(request, vacancy_id):
    """Отображение детальной информации о вакансии"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    
    # Увеличиваем счетчик просмотров
    vacancy.views_count += 1
    vacancy.save(update_fields=['views_count'])
    
    # Проверяем, подавал ли текущий пользователь заявку
    user_application = None
    if request.user.is_authenticated:
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            user_application = Application.objects.filter(vacancy=vacancy, freelancer=freelancer).first()
        except Freelancer.DoesNotExist:
            pass
    
    # Получаем похожие вакансии
    similar_vacancies = Vacancy.objects.filter(
        category=vacancy.category, 
        status='open'
    ).exclude(id=vacancy.id)[:3]
    
    context = {
        'vacancy': vacancy,
        'user_application': user_application,
        'similar_vacancies': similar_vacancies,
    }
    
    return render(request, 'vacancy/vacancy_detail.html', context)


@login_required(login_url='users:login')
def create_vacancy(request):
    """Создание новой вакансии"""
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.client = request.user
            vacancy.save()
            messages.success(request, 'Вакансия успешно создана!')
            return redirect('vacancy:vacancy_detail', vacancy_id=vacancy.id)
    else:
        form = VacancyForm()
    
    return render(request, 'vacancy/vacancy_form.html', {'form': form, 'is_edit': False})


@login_required(login_url='users:login')
def edit_vacancy(request, vacancy_id):
    """Редактирование вакансии"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, client=request.user)
    
    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=vacancy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вакансия успешно обновлена!')
            return redirect('vacancy:vacancy_detail', vacancy_id=vacancy.id)
    else:
        form = VacancyForm(instance=vacancy)
    
    return render(request, 'vacancy/vacancy_form.html', {'form': form, 'vacancy': vacancy, 'is_edit': True})


@login_required(login_url='users:login')
def delete_vacancy(request, vacancy_id):
    """Удаление вакансии"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, client=request.user)
    
    if request.method == 'POST':
        vacancy.delete()
        messages.success(request, 'Вакансия успешно удалена!')
        return redirect('vacancy:my_vacancies')
    
    return render(request, 'vacancy/vacancy_confirm_delete.html', {'vacancy': vacancy})


@login_required(login_url='users:login')
def apply_to_vacancy(request, vacancy_id):
    """Подача заявки на вакансию"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, status='open')
    
    # Проверяем, является ли пользователь фрилансером
    try:
        freelancer = Freelancer.objects.get(user=request.user)
    except Freelancer.DoesNotExist:
        messages.error(request, 'Только фрилансеры могут подавать заявки на проекты!')
        return redirect('vacancy:vacancy_detail', vacancy_id=vacancy.id)
    
    # Проверяем, не подавал ли уже заявку
    if Application.objects.filter(vacancy=vacancy, freelancer=freelancer).exists():
        messages.error(request, 'Вы уже подали заявку на этот проект!')
        return redirect('vacancy:vacancy_detail', vacancy_id=vacancy.id)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.freelancer = freelancer
            application.save()
            
            # Увеличиваем счетчик заявок
            vacancy.applications_count += 1
            vacancy.save(update_fields=['applications_count'])
            
            # Создаем уведомление
            NotificationService.create_notification(
                recipient=vacancy.client,
                notification_type_code='new_application',
                title='Новая заявка на вашу вакансию',
                message=f'Пользователь {request.user.get_full_name()} откликнулся на вашу вакансию "{vacancy.title}".',
                related_object=application,
                action_url=reverse('vacancy:application_detail', kwargs={'pk': application.pk}),
                level='info'
            )
            
            messages.success(request, 'Ваша заявка успешно отправлена!')
            return redirect('vacancy:vacancy_detail', vacancy_id=vacancy.id)
            
    else:
        form = ApplicationForm()
    return render(request, 'vacancy/application_form.html', {'form': form, 'vacancy': vacancy})

@login_required(login_url='users:login')
def application_detail(request, pk):
    """Детальная информация о заявке"""
    application = get_object_or_404(Application, pk=pk, vacancy__client=request.user)
    return render(request, 'vacancy/application_detail.html', {'application': application})


@login_required(login_url='users:login')
def my_vacancies(request):
    """Список вакансий текущего пользователя"""
    vacancies = Vacancy.objects.filter(client=request.user).order_by('-created_at')
    
    # Фильтрация по статусу
    status = request.GET.get('status')
    if status:
        vacancies = vacancies.filter(status=status)
    
    # Пагинация
    paginator = Paginator(vacancies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'selected_status': status,
    }
    
    return render(request, 'vacancy/my_vacancies.html', context)


@login_required(login_url='users:login')
def vacancy_applications(request, vacancy_id):
    """Просмотр заявок на вакансию"""
    vacancy = get_object_or_404(Vacancy, id=vacancy_id, client=request.user)
    applications = Application.objects.filter(vacancy=vacancy).order_by('-created_at')
    
    return render(request, 'vacancy/vacancy_applications.html', {
        'vacancy': vacancy,
        'applications': applications,
    })


@login_required(login_url='users:login')
def update_application_status(request, application_id, status):
    """Обновление статуса заявки"""
    application = get_object_or_404(Application, id=application_id, vacancy__client=request.user)
    
    if status in dict(Application.STATUS_CHOICES).keys():
        application.status = status
        application.save()
        
        # Если заявка принята, обновляем статус вакансии
        if status == 'accepted':
            application.vacancy.status = 'in_progress'
            application.vacancy.save()
            
        messages.success(request, f'Статус заявки обновлен на "{dict(Application.STATUS_CHOICES)[status]}"')
    
    return redirect('vacancy:vacancy_applications', vacancy_id=application.vacancy.id)


@login_required(login_url='users:login')
def my_applications(request):
    """Список заявок текущего фрилансера"""
    try:
        freelancer = Freelancer.objects.get(user=request.user)
    except Freelancer.DoesNotExist:
        messages.error(request, 'У вас нет профиля фрилансера!')
        return redirect('vacancy:vacancies_list')
    
    applications = Application.objects.filter(freelancer=freelancer).order_by('-created_at')
    
    # Фильтрация по статусу
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)
    
    # Пагинация
    paginator = Paginator(applications, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'selected_status': status,
    }
    
    return render(request, 'vacancy/my_applications.html', context)
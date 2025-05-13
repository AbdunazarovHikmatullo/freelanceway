from django.shortcuts import render
from freelancers.models import Freelancer
from vacancy.models import Vacancy

def index(request):
    freelancers = Freelancer.objects.all()

    # Преобразуем строку skills в список для каждого фрилансера
    for freelancer in freelancers:
        freelancer.skills_list = freelancer.skills.split(',') if freelancer.skills else []

    vacancies = Vacancy.objects.filter(status='open')

    context = {
        'freelancers': freelancers,
        'vacancies': vacancies
    }
    return render(request, 'main/index.html', context)


def about(request):
    return render(request, 'main/about.html')


def contacts(request):
    return render(request, 'main/contacts.html')

def page_not_found(request, exception):
    """Обработчик для страницы 404"""
    return render(request, 'main/404.html', status=404)
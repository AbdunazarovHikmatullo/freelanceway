from django.shortcuts import render



def vacancies_list(request):
    return render(request, 'vacancy/vacancies_list.html')
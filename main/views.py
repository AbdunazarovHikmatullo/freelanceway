from django.shortcuts import render

def index(request):
    return render(request, 'main/index.html')





def about(request):
    return render(request, 'main/about.html')


def contacts(request):
    return render(request, 'main/contacts.html')

def page_not_found(request, exception):
    """Обработчик для страницы 404"""
    return render(request, 'main/404.html', status=404)
from django.shortcuts import render



def freelancers_list(request):
    return render(request, 'freelancers/freelancers_list.html')
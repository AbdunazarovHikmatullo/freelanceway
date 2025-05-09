from django.urls import path
from . import views


urlpatterns = [
    path('', views.freelancers_list, name='freelancers_list'),
]
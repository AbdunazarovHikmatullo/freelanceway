from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contacts, name='contacts'),
    path('404/', views.page_not_found, name='page_not_found'),
]

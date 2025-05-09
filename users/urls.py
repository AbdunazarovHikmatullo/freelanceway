from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/<str:username>/', views.profile, name='profile'),
    # path('update_profile/', views.update_profile, name='update_profile'),
]
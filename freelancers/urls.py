from django.urls import path
from . import views

urlpatterns = [
    path('', views.freelancers_list, name='freelancers_list'),
    path('profile/create/', views.create_freelancer_profile, name='create_freelancer_profile'),
    path('profile/edit/', views.edit_freelancer_profile, name='edit_freelancer_profile'),
    path('portfolio/add/', views.add_portfolio_item, name='add_portfolio_item'),
    path('portfolio/<int:item_id>/edit/', views.edit_portfolio_item, name='edit_portfolio_item'),
    path('portfolio/<int:item_id>/delete/', views.delete_portfolio_item, name='delete_portfolio_item'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('api/featured/', views.featured_freelancers, name='featured_freelancers'),
]
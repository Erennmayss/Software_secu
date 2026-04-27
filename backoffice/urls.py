from django.urls import path

from . import views

app_name = 'backoffice'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/add/', views.recipe_create, name='recipe_create'),
    path('recipes/edit/<int:pk>/', views.recipe_update, name='recipe_update'),
    path('users/', views.user_list, name='user_list'),
    path('health/', views.health_settings, name='health_settings'),
]

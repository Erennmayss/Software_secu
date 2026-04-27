from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.index, name='index'),
    path('regime/', views.regime, name='regime'),
    path('favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
]

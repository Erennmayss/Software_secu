from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.index, name='home'),
    path('regime/', views.regime, name='regime'),
    path('favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('planner/', views.planner, name='planner'),
    path('planner/state/', views.planner_state, name='planner_state'),
    path('planner/update/', views.update_planner, name='update_planner'),
    path('fridge/ingredients/', views.fridge_ingredients_api, name='fridge_ingredients_api'),
    path('fridge/ingredients/<int:ingredient_id>/', views.fridge_ingredient_delete, name='fridge_ingredient_delete'),
]

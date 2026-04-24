from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Affiche la page vitrine à la racine du site
    path('', TemplateView.as_view(template_name='main_page.html'), name='main_page'),
    path('', include('accounts.urls')),
    path('recipes/', include('recipes.urls')),
]

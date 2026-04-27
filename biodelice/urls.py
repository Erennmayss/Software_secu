from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Page d'accueil
    path('', TemplateView.as_view(template_name='main_page.html'), name='main_page'),
    # Routes pour accounts (avec préfixe accounts/)
    path('accounts/', include('accounts.urls')),
    # Routes pour recipes
    path('recipes/', include('recipes.urls')),
    # Backoffice staff-only
    path('backoffice/', include('backoffice.urls')),
    # Route directe pour l'onboarding (solution de secours)
    path('onboarding/save/', accounts_views.save_onboarding, name='save_onboarding'),
]

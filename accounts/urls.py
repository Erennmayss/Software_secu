from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view,    name='signup'),
    path('login/',  views.login_view,     name='login'),
    path('logout/', views.logout_view,    name='logout'),
    path('onboarding/', views.onboarding_view, name='onboarding'),  
    path('onboarding/save/', views.save_onboarding, name='save_onboarding'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/save/', views.save_onboarding, name='save_settings'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('api/profile/',        views.profile_data,    name='profile_data'),
    path('api/profile/update/', views.update_profile,  name='update_profile'),
    path('api/password/request-code/', views.request_reset_code, name='request_reset_code'),
    path('api/password/confirm-code/', views.confirm_reset_code, name='confirm_reset_code'),
]

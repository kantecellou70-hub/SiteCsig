from django.urls import path
from . import views

app_name = 'oauth'

urlpatterns = [
    # Authentification
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Gestion du compte
    path('profile/', views.profile_view, name='profile'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    
    # API AJAX
    path('ajax/login/', views.ajax_login, name='ajax_login'),
    path('check-auth/', views.check_auth_status, name='check_auth_status'),
    
    # Pages légales et support
    path('terms/', views.terms_of_service_view, name='terms'),
    path('privacy/', views.privacy_policy_view, name='privacy'),
    path('support/', views.contact_support_view, name='contact_support'),
]

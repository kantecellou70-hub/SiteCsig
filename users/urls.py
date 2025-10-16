from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Tableau de bord des utilisateurs
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    
    # Gestion des utilisateurs
    path('', views.user_list, name='user_list'),
    path('create/', views.user_create, name='user_create'),
    path('<int:pk>/', views.user_detail, name='user_detail'),
    path('<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('<int:pk>/profile/', views.user_profile_edit, name='user_profile_edit'),
    
    # Gestion des rôles
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:pk>/edit/', views.role_edit, name='role_edit'),
    path('roles/<int:pk>/delete/', views.role_delete, name='role_delete'),
    
    # Invitations
    path('invite/', views.user_invitation, name='user_invitation'),
    
    # Actions en lot
    path('bulk-action/', views.bulk_user_action, name='bulk_user_action'),
    
    # API endpoints
    path('api/profile/', views.user_profile_api, name='user_profile_api'),
    path('api/search/', views.user_search_api, name='user_search_api'),
    path('api/<int:pk>/quick-edit/', views.user_quick_edit, name='user_quick_edit'),
    path('api/<int:pk>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),
]

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Если будут кастомные вью

app_name = 'users'  # Это важно!

urlpatterns = [
    # Аутентификация    
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Профиль
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),

    # Управление пользователями
    path('', views.user_list, name='user_list'),
    path('create/', views.user_create, name='user_create'),
    path('<int:pk>/', views.user_detail, name='user_detail'),
    path('<int:pk>/edit/', views.user_update, name='user_update'),
    path('<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('<int:pk>/toggle-status/', views.toggle_user_status, name='toggle_status'),

    # API
    path('api/doctors/', views.get_doctors, name='api_doctors'),
]
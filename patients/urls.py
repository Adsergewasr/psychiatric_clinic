from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'patients'

urlpatterns = [
    # Основные маршруты
    path('', views.dashboard, name='dashboard'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/create/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_update'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('patients/<int:pk>/discharge/', views.patient_discharge, name='patient_discharge'),
    
    # Экспорт
    path('patients/export/', views.patient_export, name='patient_export'),
    
    # API
    path('api/diagnoses/', views.api_diagnoses, name='api_diagnoses'),
    

]
from django.urls import path
from .views_class_based import (
    DashboardView,
    PatientListView,
    PatientDetailView,
    PatientCreateView,
    PatientUpdateView,
    PatientDeleteView,
    PatientDischargeView,
    PatientExportView,
    ApiDiagnosesView,
)

app_name = 'patients'

urlpatterns = [
    # Основные маршруты
    path('', DashboardView.as_view(), name='dashboard'),
    path('patients/', PatientListView.as_view(), name='patient_list'),
    path('patients/create/', PatientCreateView.as_view(), name='patient_create'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),
    path('patients/<int:pk>/edit/', PatientUpdateView.as_view(), name='patient_update'),
    path('patients/<int:pk>/delete/', PatientDeleteView.as_view(), name='patient_delete'),
    path('patients/<int:pk>/discharge/', PatientDischargeView.as_view(), name='patient_discharge'),
    
    # Экспорт
    path('patients/export/', PatientExportView.as_view(), name='patient_export'),
    
    # API
    path('api/diagnoses/', ApiDiagnosesView.as_view(), name='api_diagnoses'),
    

]
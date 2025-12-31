from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .admin import discharge_patient_view

app_name = 'patients'

urlpatterns = [
    # Кастомные админ-вью
    path(
        'admin/patients/patient/<int:patient_id>/discharge/',
        login_required(discharge_patient_view),
        name='patient_discharge'
    ),
]
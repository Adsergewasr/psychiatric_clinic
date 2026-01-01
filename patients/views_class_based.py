from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from users.mixins import RoleRequiredMixin, PermissionRequiredMixin, ObjectPermissionMixin
from .models import Patient
from .forms import PatientForm



class PatientListView(RoleRequiredMixin, ListView):
    """Список пациентов (классовое представление)"""
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 25
    allowed_roles = ['ADMIN', 'DOCTOR', 'NURSE', 'REGISTRAR', 'ANALYST']
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('attending_physician')
        # Фильтрация по правам доступа
        if not self.request.user.is_administrator:
            if self.request.user.is_doctor:
                queryset = queryset.filter(attending_physician=self.request.user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем форму поиска и другие данные при необходимости
        return context


class PatientDetailView(ObjectPermissionMixin, DetailView):
    """Просмотр карты пациента (классовое представление)"""
    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()
        context['hospitalizations'] = patient.hospitalizations.all()
        context['can_edit'] = patient.user_can_edit(self.request.user)
        context['can_delete'] = patient.user_can_delete(self.request.user)
        context['can_discharge'] = (patient.status == 'HOSPITALIZED' and patient.user_can_edit(self.request.user))
        return context


class PatientCreateView(RoleRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    allowed_roles = ['ADMIN', 'DOCTOR', 'NURSE', 'REGISTRAR']
    success_url = reverse_lazy('patients:patient_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Пациент успешно добавлен')
        return super().form_valid(form)


class PatientUpdateView(ObjectPermissionMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patients:patient_list')

    def form_valid(self, form):
        messages.success(self.request, 'Данные пациента обновлены')
        return super().form_valid(form)


class PatientDeleteView(ObjectPermissionMixin, DeleteView):
    model = Patient
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patients:patient_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Пациент удалён')
        return super().delete(request, *args, **kwargs)

# Для будущего: можно добавить CBV для discharge, export и др.

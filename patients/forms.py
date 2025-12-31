from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Patient, Diagnosis

User = get_user_model()


class PatientForm(forms.ModelForm):
    """Форма для создания и редактирования пациента"""
    
    class Meta:
        model = Patient
        fields = '__all__'  # Временно используем все поля
        
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'birth_place': forms.TextInput(attrs={'class': 'form-control'}),
            'citizenship': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_series': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_issued_by': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'passport_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'snils': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_policy': forms.TextInput(attrs={'class': 'form-control'}),
            'workplace': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'admission_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'admission_from': forms.TextInput(attrs={'class': 'form-control'}),
            'delivered_by': forms.TextInput(attrs={'class': 'form-control'}),
            'referral_diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'admission_diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'admission_mkb_code': forms.TextInput(attrs={'class': 'form-control'}),
            'attending_physician': forms.Select(attrs={'class': 'form-select'}),
            'discharge_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'discharge_diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'discharge_mkb_code': forms.TextInput(attrs={'class': 'form-control'}),
            'outcome': forms.Select(attrs={'class': 'form-select'}),
            'work_capacity': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Убираем поле created_by из формы - оно будет устанавливаться автоматически
        if 'created_by' in self.fields:
            del self.fields['created_by']
        
        # Убираем поле case_number из формы - оно генерируется автоматически
        if 'case_number' in self.fields:
            del self.fields['case_number']
    
    def save(self, commit=True):
        """Сохранение формы с указанием создателя"""
        patient = super().save(commit=False)
        
        # Устанавливаем создателя, если это новый пациент
        if not patient.pk and self.user:
            patient.created_by = self.user
        
        if commit:
            patient.save()
        
        return patient


# Остальные формы оставляем как есть
class PatientSearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Поиск по ФИО, номеру истории, паспорту...'
    }))
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Все статусы')] + Patient.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    gender = forms.ChoiceField(
        required=False,
        choices=[('', 'Все')] + Patient.Gender.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'С даты'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'По дату'
        })
    )


class PatientExportForm(forms.Form):
    """Форма выбора пациентов для экспорта"""
    patients = forms.ModelMultipleChoiceField(
        queryset=Patient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    export_format = forms.ChoiceField(
        choices=[
            ('csv', 'CSV'),
            ('xlsx', 'Excel (XLSX)'),
            ('json', 'JSON'),
        ],
        initial='xlsx',
        widget=forms.RadioSelect
    )
    
    include_fields = forms.MultipleChoiceField(
        choices=[
            ('basic', 'Основные данные'),
            ('documents', 'Документы'),
            ('hospitalization', 'Данные госпитализации'),
            ('discharge', 'Данные выписки'),
            ('notes', 'Примечания'),
        ],
        initial=['basic', 'documents', 'hospitalization'],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
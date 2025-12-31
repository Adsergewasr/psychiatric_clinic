from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Patient, Hospitalization, Diagnosis


class PatientResource(resources.ModelResource):
    class Meta:
        model = Patient
        exclude = ('id',)
        import_id_fields = ['case_number']


class HospitalizationInline(admin.TabularInline):
    model = Hospitalization
    extra = 0
    fields = ['admission_date', 'discharge_date', 'diagnosis', 'department']
    readonly_fields = ['admission_date', 'discharge_date']


@admin.register(Patient)
class PatientAdmin(ImportExportModelAdmin):
    resource_class = PatientResource
    list_display = ['case_number', 'full_name', 'gender_display', 'admission_date_short', 'status_display', 'view_button']
    search_fields = ['case_number', 'last_name', 'first_name', 'middle_name', 'phone']
    list_filter = ['status', 'gender', 'admission_date']
    fieldsets = (
        ('Общие сведения', {
            'fields': (
                'case_number',
                ('last_name', 'first_name', 'middle_name'),
                ('gender', 'birth_date'),
                'address',
                'phone',
            )
        }),
        ('Документы', {
            'fields': (
                ('passport_series', 'passport_number'),
                'snils',
                'insurance_policy',
            ),
            'classes': ('collapse',),
        }),
        ('Госпитализация', {
            'fields': (
                'admission_date',
                'admission_from',
                'admission_diagnosis',
                'admission_mkb_code',
                'attending_physician',
            )
        }),
        ('Выписка', {
            'fields': (
                'discharge_date',
                'discharge_diagnosis',
                'discharge_mkb_code',
                'outcome',
                'status',
            )
        }),
    )
    
    readonly_fields = ['case_number']
    inlines = [HospitalizationInline]
    autocomplete_fields = ['attending_physician']
    
    def full_name(self, obj):
        return f'{obj.last_name} {obj.first_name} {obj.middle_name}'
    full_name.short_description = 'ФИО'
    
    def gender_display(self, obj):
        return obj.get_gender_display()
    gender_display.short_description = 'Пол'
    
    def admission_date_short(self, obj):
        return obj.admission_date.strftime('%d.%m.%Y')
    admission_date_short.short_description = 'Поступил'
    
    def status_display(self, obj):
        colors = {
            'HOSPITALIZED': 'orange',
            'DISCHARGED': 'green',
            'TRANSFERRED': 'blue',
            'DIED': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Статус'
    
    def view_button(self, obj):
        url = reverse('admin:patients_patient_change', args=[obj.id])
        return format_html('<a href="{}" class="button">Просмотр</a>', url)
    view_button.short_description = 'Действия'


@admin.register(Hospitalization)
class HospitalizationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'admission_date', 'discharge_date', 'department']
    search_fields = ['patient__last_name', 'patient__first_name', 'diagnosis']


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'description_short']
    search_fields = ['code', 'name']
    
    def description_short(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_short.short_description = 'Описание'
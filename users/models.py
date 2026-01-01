from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from .managers import UserManager 

class User(AbstractUser):
    """Кастомная модель пользователя с расширенными полями"""
    
    # Заменяем стандартный менеджер
    objects = UserManager()

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Администратор'
        DOCTOR = 'DOCTOR', 'Врач'
        NURSE = 'NURSE', 'Медсестра'
        REGISTRAR = 'REGISTRAR', 'Регистратор'
        ANALYST = 'ANALYST', 'Аналитик'
    
    # Основные поля
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=Role.choices,
        default=Role.DOCTOR
    )
    
    # Контактная информация
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+79991234567'. До 15 цифр."
    )
    phone = models.CharField(
        'Телефон',
        validators=[phone_regex],
        max_length=17,
        blank=True
    )
    
    # Медицинская информация
    medical_license = models.CharField(
        'Медицинская лицензия',
        max_length=50,
        blank=True
    )
    
    specialization = models.CharField(
        'Специализация',
        max_length=200,
        blank=True
    )
    
    department = models.CharField(
        'Отделение',
        max_length=100,
        blank=True
    )
    
    # Дополнительные поля
    birth_date = models.DateField(
        'Дата рождения',
        null=True,
        blank=True
    )
    
    hire_date = models.DateField(
        'Дата приема на работу',
        null=True,
        blank=True
    )
    
    is_active = models.BooleanField(
        'Активен',
        default=True,
        help_text='Отметьте, если пользователь должен считаться активным. '
                  'Уберите отметку вместо удаления учётной записи.'
    )
    
    notes = models.TextField(
        'Примечания',
        blank=True
    )
    
    # Системные поля
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        'Дата обновления',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']
        permissions = [
            ('can_view_statistics', 'Может просматривать статистику'),
            ('can_export_data', 'Может экспортировать данные'),
            ('can_manage_users', 'Может управлять пользователями'),
            ('can_view_all_patients', 'Может просматривать всех пациентов'),
            ('can_edit_all_patients', 'Может редактировать всех пациентов'),
        ]
    
    def __str__(self):
        return f'{self.get_full_name()} ({self.get_role_display()})'
    
    @property
    def is_administrator(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR
    
    @property
    def is_nurse(self):
        return self.role == self.Role.NURSE
    
    @property
    def is_registrar(self):
        return self.role == self.Role.REGISTRAR
    
    @property
    def is_analyst(self):
        return self.role == self.Role.ANALYST
    
    def get_permission_codenames(self):
        """Получить список кодов разрешений пользователя"""
        permissions = []
        
        # Разрешения на основе роли
        if self.is_administrator:
            permissions.extend([
                'patients.add_patient',
                'patients.change_patient',
                'patients.delete_patient',
                'patients.view_patient',
                'users.can_manage_users',
                'users.can_view_statistics',
                'users.can_export_data',
                'users.can_view_all_patients',
                'users.can_edit_all_patients',
            ])
        elif self.is_doctor:
            permissions.extend([
                'patients.add_patient',
                'patients.change_patient',
                'patients.view_patient',
                'users.can_export_data',
            ])
        elif self.is_nurse:
            permissions.extend([
                'patients.add_patient',
                'patients.view_patient',
            ])
        elif self.is_registrar:
            permissions.extend([
                'patients.add_patient',
                'patients.view_patient',
            ])
        elif self.is_analyst:
            permissions.extend([
                'patients.view_patient',
                'users.can_view_statistics',
                'users.can_export_data',
            ])
        
        return permissions


class UserProfile(models.Model):
    """Профиль пользователя для дополнительных данных"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    
    # Личная информация
    middle_name = models.CharField(
        'Отчество',
        max_length=100,
        blank=True
    )
    
    photo = models.ImageField(
        'Фотография',
        upload_to='users/photos/',
        blank=True,
        null=True
    )
    
    signature = models.ImageField(
        'Подпись',
        upload_to='users/signatures/',
        blank=True,
        null=True,
        help_text='Электронная подпись для документов'
    )
    
    # Профессиональная информация
    education = models.TextField(
        'Образование',
        blank=True
    )
    
    qualifications = models.TextField(
        'Квалификации',
        blank=True
    )
    
    experience_years = models.PositiveIntegerField(
        'Стаж работы (лет)',
        default=0
    )
    
    # Настройки пользователя
    theme = models.CharField(
        'Тема интерфейса',
        max_length=20,
        choices=[
            ('light', 'Светлая'),
            ('dark', 'Темная'),
            ('auto', 'Авто'),
        ],
        default='light'
    )
    
    language = models.CharField(
        'Язык интерфейса',
        max_length=10,
        choices=[
            ('ru', 'Русский'),
            ('en', 'English'),
        ],
        default='ru'
    )
    
    # Системные поля
    last_login_ip = models.GenericIPAddressField(
        'Последний IP входа',
        blank=True,
        null=True
    )
    
    last_activity = models.DateTimeField(
        'Последняя активность',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f'Профиль: {self.user}'
    
    @property
    def full_name(self):
        """Полное ФИО"""
        parts = [self.user.last_name, self.user.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)


class LoginHistory(models.Model):
    """История входов пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history',
        verbose_name='Пользователь'
    )
    
    login_time = models.DateTimeField(
        'Время входа',
        auto_now_add=True
    )
    
    ip_address = models.GenericIPAddressField(
        'IP адрес'
    )
    
    user_agent = models.TextField(
        'User Agent',
        blank=True
    )
    
    success = models.BooleanField(
        'Успешный вход',
        default=True
    )
    
    failure_reason = models.CharField(
        'Причина неудачи',
        max_length=200,
        blank=True
    )
    
    class Meta:
        verbose_name = 'История входа'
        verbose_name_plural = 'История входов'
        ordering = ['-login_time']
    
    def __str__(self):
        status = "Успешно" if self.success else "Неудачно"
        return f'{self.user} - {self.login_time} ({status})'
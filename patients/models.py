from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Patient(models.Model):
    """Модель пациента по форме №003/у"""
    
    class Gender(models.TextChoices):
        MALE = 'M', 'Мужской'
        FEMALE = 'F', 'Женский'
    
    class MaritalStatus(models.TextChoices):
        SINGLE = 'S', 'Холост/Не замужем'
        MARRIED = 'M', 'Женат/Замужем'
        DIVORCED = 'D', 'Разведен(а)'
        WIDOWED = 'W', 'Вдовец/Вдова'
    
    class Education(models.TextChoices):
        NONE = 'N', 'Нет образования'
        PRIMARY = 'P', 'Начальное'
        SECONDARY = 'S', 'Среднее'
        SPECIAL = 'SP', 'Среднее специальное'
        HIGHER = 'H', 'Высшее'
        UNFINISHED_HIGHER = 'UH', 'Неоконченное высшее'
    
        @property
        def full_name(self):
            """Полное ФИО пациента"""
            parts = [self.last_name, self.first_name]
            if self.middle_name:
                parts.append(self.middle_name)
            return ' '.join(parts)
        
    # === РАЗДЕЛ 1: ОБЩИЕ СВЕДЕНИЯ ===
    # 1. Фамилия, имя, отчество
    last_name = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    
    # 2. Пол
    gender = models.CharField(
        'Пол',
        max_length=1,
        choices=Gender.choices,
        default=Gender.MALE
    )
    
    # 3. Дата рождения
    birth_date = models.DateField('Дата рождения')
    
    # 4. Возраст (будем вычислять автоматически)
    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
    
    # 5. Место рождения
    birth_place = models.CharField('Место рождения', max_length=255, blank=True)
    
    # 6. Гражданство
    citizenship = models.CharField('Гражданство', max_length=100, default='РФ')
    
    # 7. Адрес постоянного места жительства
    address = models.TextField('Адрес постоянного места жительства')
    
    # 8. Место работы, должность
    workplace = models.CharField('Место работы', max_length=255, blank=True)
    position = models.CharField('Должность', max_length=255, blank=True)
    
    # 9. Профессия
    profession = models.CharField('Профессия', max_length=255, blank=True)
    
    # 10. Семейное положение
    marital_status = models.CharField(
        'Семейное положение',
        max_length=2,
        choices=MaritalStatus.choices,
        default=MaritalStatus.SINGLE
    )
    
    # 11. Образование
    education = models.CharField(
        'Образование',
        max_length=2,
        choices=Education.choices,
        default=Education.SECONDARY
    )
    
    # === РАЗДЕЛ 2: ДАННЫЕ О ГОСПИТАЛИЗАЦИИ ===
    # 12. Дата поступления
    admission_date = models.DateTimeField('Дата и время поступления', default=timezone.now)
    
    # 13. Откуда поступил
    admission_from = models.CharField('Откуда поступил', max_length=255, blank=True)
    
    # 14. Кем доставлен
    delivered_by = models.CharField('Кем доставлен', max_length=255, blank=True)
    
    # 15. Диагноз направившего учреждения
    referral_diagnosis = models.TextField('Диагноз направившего учреждения', blank=True)
    
    # 16. Диагноз при поступлении
    admission_diagnosis = models.TextField('Диагноз при поступлении')
    
    # 17. Код по МКБ-10 при поступлении
    admission_mkb_code = models.CharField('Код МКБ-10 при поступлении', max_length=20, blank=True)
    
    # === РАЗДЕЛ 3: ДАННЫЕ О ЛЕЧЕНИИ ===
    # 18. Лечащий врач
    attending_physician = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients',
        verbose_name='Лечащий врач'
    )
    
    # 19. Дата выписки
    discharge_date = models.DateTimeField('Дата выписки', null=True, blank=True)
    
    # 20. Диагноз при выписке
    discharge_diagnosis = models.TextField('Диагноз при выписке', blank=True)
    
    # 21. Код по МКБ-10 при выписке
    discharge_mkb_code = models.CharField('Код МКБ-10 при выписке', max_length=20, blank=True)
    
    # 22. Исход заболевания
    OUTCOME_CHOICES = [
        ('RECOVERY', 'Выздоровление'),
        ('IMPROVEMENT', 'Улучшение'),
        ('NO_CHANGE', 'Без изменений'),
        ('DETERIORATION', 'Ухудшение'),
        ('DEATH', 'Смерть'),
        ('TRANSFER', 'Перевод в другую организацию'),
    ]
    outcome = models.CharField('Исход заболевания', max_length=20, choices=OUTCOME_CHOICES, blank=True)
    
    # 23. Трудоспособность
    WORK_CAPACITY_CHOICES = [
        ('RESTORED', 'Восстановлена'),
        ('IMPROVED', 'Улучшена'),
        ('NO_CHANGE', 'Без изменений'),
        ('DISABLED', 'Установлена инвалидность'),
    ]
    work_capacity = models.CharField('Трудоспособность', max_length=20, choices=WORK_CAPACITY_CHOICES, blank=True)
    
    # === ДОПОЛНИТЕЛЬНЫЕ ПОЛЯ ===
    # 24. Примечания
    notes = models.TextField('Примечания', blank=True)
    
    # 25. Статус пациента
    STATUS_CHOICES = [
        ('HOSPITALIZED', 'Госпитализирован'),
        ('DISCHARGED', 'Выписан'),
        ('TRANSFERRED', 'Переведен'),
        ('DIED', 'Умер'),
    ]
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='HOSPITALIZED'
    )
    
    # 26. Номер истории болезни (уникальный)
    case_number = models.CharField(
        'Номер истории болезни',
        max_length=50,
        unique=True,
        editable=False
    )
    
    # 27. Контактный телефон
    phone = models.CharField('Контактный телефон', max_length=20, blank=True)
    
    # 28. Паспортные данные
    passport_series = models.CharField('Серия паспорта', max_length=10, blank=True)
    passport_number = models.CharField('Номер паспорта', max_length=20, blank=True)
    passport_issued_by = models.TextField('Кем выдан паспорт', blank=True)
    passport_issue_date = models.DateField('Дата выдачи паспорта', null=True, blank=True)
    
    # 29. Страховой полис
    insurance_policy = models.CharField('Страховой полис', max_length=50, blank=True)
    
    # 30. СНИЛС
    snils = models.CharField('СНИЛС', max_length=14, blank=True)
    
    # Системные поля
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_patients',
        verbose_name='Кем создана запись'
    )
    
    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'
        ordering = ['-admission_date']
        indexes = [
            models.Index(fields=['last_name', 'first_name', 'middle_name']),
            models.Index(fields=['admission_date']),
            models.Index(fields=['status']),
            models.Index(fields=['case_number']),
        ]
    
    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name} (ИБ: {self.case_number})'
    
    def save(self, *args, **kwargs):
        if not self.case_number:
            # Генерируем номер истории болезни: Год-ПорядковыйНомер
            year = timezone.now().year
            last_case = Patient.objects.filter(case_number__startswith=f'{year}-').order_by('case_number').last()
            
            if last_case:
                last_num = int(last_case.case_number.split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.case_number = f'{year}-{new_num:04d}'
        
        super().save(*args, **kwargs)


class Hospitalization(models.Model):
    """Модель для учета повторных госпитализаций"""
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='hospitalizations',
        verbose_name='Пациент'
    )
    admission_date = models.DateField('Дата поступления')
    discharge_date = models.DateField('Дата выписки', null=True, blank=True)
    diagnosis = models.TextField('Диагноз')
    mkb_code = models.CharField('Код МКБ-10', max_length=20, blank=True)
    department = models.CharField('Отделение', max_length=100)
    attending_physician = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Лечащий врач'
    )
    outcome = models.CharField('Исход', max_length=50, blank=True)
    notes = models.TextField('Примечания', blank=True)
    
    class Meta:
        verbose_name = 'Госпитализация'
        verbose_name_plural = 'Госпитализации'
        ordering = ['-admission_date']
    
    def __str__(self):
        return f'{self.patient} - {self.admission_date}'


class Diagnosis(models.Model):
    """Справочник диагнозов МКБ-10"""
    code = models.CharField('Код МКБ-10', max_length=10, unique=True)
    name = models.CharField('Наименование диагноза', max_length=500)
    description = models.TextField('Описание', blank=True)
    
    class Meta:
        verbose_name = 'Диагноз МКБ-10'
        verbose_name_plural = 'Диагнозы МКБ-10'
        ordering = ['code']
    
    def __str__(self):
        return f'{self.code} - {self.name[:50]}'
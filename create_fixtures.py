import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychiatric_hospital.settings')
django.setup()

from users.models import User
from patients.models import Patient, Hospitalization

# Создание тестовых пользователей
for i in range(5):
    user, created = User.objects.get_or_create(
        username=f'doctor{i+1}',
        defaults={
            'email': f'doctor{i+1}@test.com',
            'role': 'DOCTOR',
            'is_staff': True,
            'is_superuser': False,
            'first_name': f'Имя{i+1}',
            'last_name': f'Фамилия{i+1}',
            'phone': f'+7999123456{i}',
        }
    )
    if created:
        user.set_password('testpassword')
        user.save()


# Создание тестовых пациентов с карточками, госпитализациями и движениями
status_choices = ['HOSPITALIZED', 'DISCHARGED', 'TRANSFERRED', 'DIED']
outcome_choices = ['RECOVERY', 'IMPROVEMENT', 'NO_CHANGE', 'DETERIORATION', 'DEATH', 'TRANSFER']
departments = ['Психиатрия', 'Неврология', 'Терапия', 'Реанимация']
diagnoses = ['Шизофрения', 'Депрессия', 'Биполярное расстройство', 'Психоз', 'Невроз', 'Паранойя', 'Аутизм']

for i in range(7):
    patient = Patient.objects.create(
        last_name=f'Пациент{i+1}',
        first_name=f'Имя{i+1}',
        middle_name=f'Отчество{i+1}',
        gender=random.choice(['M', 'F']),
        birth_date=date(1980+i, random.randint(1,12), random.randint(1,28)),
        birth_place=f'Город {i+1}',
        citizenship='РФ',
        address=f'Город, улица {i+1}',
        workplace='Завод',
        position='Слесарь',
        profession='Работник',
        marital_status=random.choice(['S', 'M', 'D', 'W']),
        education=random.choice(['N', 'P', 'S', 'SP', 'H', 'UH']),
        phone=f'+79991234{i+10}',
        passport_series=f'{random.randint(1000,9999)}',
        passport_number=f'{random.randint(100000,999999)}',
        passport_issued_by=f'ОВД {i+1}',
        passport_issue_date=date(2000+i, random.randint(1,12), random.randint(1,28)),
        insurance_policy=f'{random.randint(1000000000000,9999999999999)}',
        snils=f'{random.randint(10000000000,99999999999)}',
        created_by=User.objects.first(),
        status=random.choice(status_choices),
        notes='Тестовая карточка пациента',
    )

    # Истории госпитализаций (по 5-7 на пациента)
    for j in range(random.randint(5,7)):
        adm_date = date.today() - timedelta(days=random.randint(30, 365))
        dis_date = adm_date + timedelta(days=random.randint(5, 30))
        Hospitalization.objects.create(
            patient=patient,
            admission_date=adm_date,
            discharge_date=dis_date,
            diagnosis=random.choice(diagnoses),
            mkb_code=f'F{random.randint(20,99)}',
            department=random.choice(departments),
            attending_physician=User.objects.order_by('?').first(),
            outcome=random.choice(outcome_choices),
            notes=f'Госпитализация {j+1} пациента {i+1}'
        )

print('Тестовые карточки, госпитализации и движения успешно созданы!')
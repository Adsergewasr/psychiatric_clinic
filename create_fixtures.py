import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychiatric_hospital.settings')
django.setup()

from patients.models import Diagnosis

diagnoses_data = [
    {
        "code": "F20",
        "name": "Шизофрения",
        "description": "Группа психических расстройств с нарушениями мышления, восприятия и эмоциональных реакций"
    },
    {
        "code": "F31",
        "name": "Биполярное аффективное расстройство",
        "description": "Расстройство, характеризующееся чередованием эпизодов мании и депрессии"
    },
    {
        "code": "F32",
        "name": "Депрессивный эпизод",
        "description": "Психическое расстройство, характеризующееся сниженным настроением, ангедонией и упадком сил"
    },
    {
        "code": "F41",
        "name": "Другие тревожные расстройства",
        "description": "Расстройства, при которых тревога является основным симптомом"
    },
    {
        "code": "F43",
        "name": "Реакция на тяжелый стресс и нарушения адаптации",
        "description": "Расстройства, возникающие в ответ на стрессовое событие"
    },
    {
        "code": "F60",
        "name": "Расстройства личности",
        "description": "Длительные модели поведения и внутренних переживаний, отклоняющиеся от культурных норм"
    },
    {
        "code": "F84",
        "name": "Общие расстройства психологического развития",
        "description": "Расстройства аутистического спектра"
    },
    {
        "code": "F10",
        "name": "Психические и поведенческие расстройства, вызванные употреблением алкоголя",
        "description": "Расстройства, связанные с употреблением алкоголя"
    },
    {
        "code": "F70",
        "name": "Легкая умственная отсталость",
        "description": "IQ 50-69"
    },
    {
        "code": "F71",
        "name": "Умеренная умственная отсталость",
        "description": "IQ 35-49"
    }
]

# Создаем объекты в базе данных
for data in diagnoses_data:
    Diagnosis.objects.get_or_create(
        code=data['code'],
        defaults={
            'name': data['name'],
            'description': data['description']
        }
    )

print(f"Создано {len(diagnoses_data)} диагнозов в базе данных")

# Теперь создаем фикстуру
fixtures = []
for i, diagnosis in enumerate(Diagnosis.objects.all(), 1):
    fixtures.append({
        "model": "patients.diagnosis",
        "pk": i,
        "fields": {
            "code": diagnosis.code,
            "name": diagnosis.name,
            "description": diagnosis.description
        }
    })

# Сохраняем в файл
with open('patients/fixtures/diagnoses.json', 'w', encoding='utf-8') as f:
    json.dump(fixtures, f, ensure_ascii=False, indent=2)

print("Фикстура сохранена в patients/fixtures/diagnoses.json")
#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Добавляем путь к проекту в sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Пытаемся определить правильное название модуля настроек
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychiatric_clinic.settings')
    django.setup()
except Exception as e:
    print(f"Ошибка при первой попытке: {e}")
    print("Пробуем другие варианты...")
    
    # Попробуем найти settings.py
    possible_settings = [
        'psychiatric_clinic.settings',
        'clinic.settings', 
        'psych_clinic.settings',
        'settings',
    ]
    
    for setting in possible_settings:
        try:
            os.environ['DJANGO_SETTINGS_MODULE'] = setting
            django.setup()
            print(f"✓ Найден модуль настроек: {setting}")
            break
        except:
            continue
    else:
        print("Не удалось найти модуль настроек Django.")
        print("Поиск файлов settings.py...")
        
        # Ищем settings.py в проекте
        for root, dirs, files in os.walk(project_root):
            if 'settings.py' in files:
                # Определяем путь к модулю настроек
                rel_path = os.path.relpath(root, project_root)
                if rel_path == '.':
                    module_name = os.path.basename(project_root)
                else:
                    module_name = rel_path.replace(os.sep, '.')
                
                settings_module = f"{module_name}.settings" if module_name else "settings"
                try:
                    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
                    django.setup()
                    print(f"✓ Найден и загружен: {settings_module}")
                    break
                except:
                    continue
        
        # Если ничего не нашли
        try:
            django.setup()
        except Exception as final_error:
            print(f"Критическая ошибка: {final_error}")
            print("\nРучная настройка:")
            print("1. Убедитесь, что manage.py находится в этой же директории")
            print("2. Проверьте название проекта в settings.py")
            sys.exit(1)

from django.contrib.auth import get_user_model
from patients.models import Patient, Diagnosis

User = get_user_model()

def create_sample_data():
    print("="*60)
    print("Создание тестовых данных для психиатрической клиники")
    print("="*60)
    
    # 1. Проверяем соединение с БД
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Соединение с базой данных установлено")
    except Exception as e:
        print(f"✗ Ошибка соединения с БД: {e}")
        return
    
    # 2. Создаем суперпользователя если нет
    print("\n1. Создание пользователей...")
    
    if not User.objects.filter(username='admin').exists():
        try:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@clinic.ru',
                password='admin123',
                first_name='Алексей',
                last_name='Петров',
                role='ADMIN'
            )
            print(f"  ✓ Создан администратор: {admin.username} (пароль: admin123)")
        except Exception as e:
            print(f"  ✗ Ошибка создания администратора: {e}")
            # Попробуем создать обычного пользователя
            admin = User.objects.create_user(
                username='admin',
                email='admin@clinic.ru',
                password='admin123',
                first_name='Алексей',
                last_name='Петров',
                role='ADMIN',
                is_staff=True,
                is_superuser=True
            )
            print(f"  ✓ Администратор создан альтернативным способом")
    else:
        admin = User.objects.get(username='admin')
        print(f"  ✓ Администратор уже существует: {admin.username}")
    
    # 3. Создаем врачей
    doctors_data = [
        {'username': 'doctor1', 'first_name': 'Ирина', 'last_name': 'Сидорова', 'role': 'DOCTOR'},
        {'username': 'doctor2', 'first_name': 'Михаил', 'last_name': 'Козлов', 'role': 'DOCTOR'},
        {'username': 'doctor3', 'first_name': 'Елена', 'last_name': 'Волкова', 'role': 'DOCTOR'},
    ]
    
    doctors = []
    for data in doctors_data:
        if not User.objects.filter(username=data['username']).exists():
            try:
                doctor = User.objects.create_user(
                    username=data['username'],
                    email=f"{data['username']}@clinic.ru",
                    password='doctor123',
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    role=data['role'],
                    is_staff=True
                )
                doctors.append(doctor)
                print(f"  ✓ Создан врач: {doctor.username} (пароль: doctor123)")
            except Exception as e:
                print(f"  ✗ Ошибка создания врача {data['username']}: {e}")
        else:
            doctor = User.objects.get(username=data['username'])
            doctors.append(doctor)
            print(f"  ✓ Врач уже существует: {doctor.username}")
    
    # 4. Создаем других пользователей
    other_users_data = [
        {'username': 'nurse1', 'first_name': 'Ольга', 'last_name': 'Иванова', 'role': 'NURSE'},
        {'username': 'registrar1', 'first_name': 'Дмитрий', 'last_name': 'Смирнов', 'role': 'REGISTRAR'},
        {'username': 'analyst1', 'first_name': 'Анна', 'last_name': 'Попова', 'role': 'ANALYST'},
    ]
    
    for data in other_users_data:
        if not User.objects.filter(username=data['username']).exists():
            try:
                user = User.objects.create_user(
                    username=data['username'],
                    email=f"{data['username']}@clinic.ru",
                    password=f"{data['role'].lower()}123",
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    role=data['role'],
                    is_staff=True
                )
                print(f"  ✓ Создан {data['role']}: {user.username} (пароль: {data['role'].lower()}123)")
            except Exception as e:
                print(f"  ✗ Ошибка создания {data['role']} {data['username']}: {e}")
    
    # 5. Создаем диагнозы
    print("\n2. Создание диагнозов МКБ-10...")
    
    diagnoses_data = [
        {"code": "F20.0", "name": "Параноидная шизофрения", "description": "Хроническое психическое расстройство"},
        {"code": "F20.1", "name": "Гебефреническая шизофрения", "description": "Шизофрения с эмоциональными нарушениями"},
        {"code": "F31", "name": "Биполярное аффективное расстройство", "description": "Расстройство с чередованием маниакальных и депрессивных эпизодов"},
        {"code": "F32.0", "name": "Легкий депрессивный эпизод", "description": "Депрессивный эпизод легкой степени"},
        {"code": "F32.1", "name": "Умеренный депрессивный эпизод", "description": "Депрессивный эпизод средней степени"},
        {"code": "F32.2", "name": "Тяжелый депрессивный эпизод", "description": "Тяжелый депрессивный эпизод"},
        {"code": "F41.0", "name": "Паническое расстройство", "description": "Повторные панические атаки"},
        {"code": "F41.1", "name": "Генерализованное тревожное расстройство", "description": "Хроническая тревога"},
        {"code": "F42", "name": "Обсессивно-компульсивное расстройство", "description": "Навязчивые мысли и действия"},
        {"code": "F43.0", "name": "Острая реакция на стресс", "description": "Реакция на стрессовое событие"},
        {"code": "F43.1", "name": "Посттравматическое стрессовое расстройство", "description": "ПТСР"},
        {"code": "F48.0", "name": "Неврастения", "description": "Повышенная утомляемость, раздражительность"},
        {"code": "F60.0", "name": "Параноидное расстройство личности", "description": "Подозрительность, недоверчивость"},
    ]
    
    created_diagnoses = 0
    for data in diagnoses_data:
        try:
            diagnosis, created = Diagnosis.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'description': data['description']
                }
            )
            if created:
                created_diagnoses += 1
                print(f"  ✓ Диагноз: {diagnosis.code} - {diagnosis.name}")
        except Exception as e:
            print(f"  ✗ Ошибка создания диагноза {data['code']}: {e}")
    
    print(f"  Всего создано диагнозов: {created_diagnoses}")
    
    # 6. Создаем пациентов
    print("\n3. Создание пациентов...")
    
    patients_data = [
        {
            'last_name': 'Иванов', 'first_name': 'Иван', 'middle_name': 'Иванович',
            'gender': 'M', 'birth_date': '1985-05-15', 
            'diagnosis': 'F41.1 Генерализованное тревожное расстройство',
            'mkb_code': 'F41.1',
            'status': 'HOSPITALIZED', 
            'doctor': doctors[0] if doctors else admin,
            'admission_from': 'Самообращение'
        },
        {
            'last_name': 'Петрова', 'first_name': 'Анна', 'middle_name': 'Сергеевна',
            'gender': 'F', 'birth_date': '1992-08-22',
            'diagnosis': 'F32.1 Умеренный депрессивный эпизод',
            'mkb_code': 'F32.1',
            'status': 'DISCHARGED', 
            'doctor': doctors[0] if doctors else admin,
            'admission_from': 'Поликлиника №5'
        },
        {
            'last_name': 'Сидоров', 'first_name': 'Алексей', 'middle_name': 'Петрович',
            'gender': 'M', 'birth_date': '1978-03-10',
            'diagnosis': 'F20.0 Параноидная шизофрения',
            'mkb_code': 'F20.0',
            'status': 'HOSPITALIZED', 
            'doctor': doctors[0] if doctors else admin,
            'admission_from': 'Скорая помощь'
        },
        {
            'last_name': 'Кузнецова', 'first_name': 'Елена', 'middle_name': 'Владимировна',
            'gender': 'F', 'birth_date': '1965-11-30',
            'diagnosis': 'F48.0 Неврастения',
            'mkb_code': 'F48.0',
            'status': 'DISCHARGED', 
            'doctor': doctors[1] if len(doctors) > 1 else admin,
            'admission_from': 'Самообращение'
        },
        {
            'last_name': 'Волков', 'first_name': 'Дмитрий', 'middle_name': 'Александрович',
            'gender': 'M', 'birth_date': '1995-07-08',
            'diagnosis': 'F41.0 Паническое расстройство',
            'mkb_code': 'F41.0',
            'status': 'HOSPITALIZED', 
            'doctor': doctors[1] if len(doctors) > 1 else admin,
            'admission_from': 'Поликлиника вуза'
        },
        {
            'last_name': 'Смирнова', 'first_name': 'Ольга', 'middle_name': 'Игоревна',
            'gender': 'F', 'birth_date': '1980-12-14',
            'diagnosis': 'F43.1 Посттравматическое стрессовое расстройство',
            'mkb_code': 'F43.1',
            'status': 'DISCHARGED', 
            'doctor': doctors[0] if doctors else admin,
            'admission_from': 'Самообращение'
        },
        {
            'last_name': 'Попов', 'first_name': 'Сергей', 'middle_name': 'Николаевич',
            'gender': 'M', 'birth_date': '1970-04-25',
            'diagnosis': 'F20.0 Параноидная шизофрения',
            'mkb_code': 'F20.0',
            'status': 'HOSPITALIZED', 
            'doctor': doctors[2] if len(doctors) > 2 else admin,
            'admission_from': 'Скорая помощь'
        },
        {
            'last_name': 'Федорова', 'first_name': 'Мария', 'middle_name': 'Дмитриевна',
            'gender': 'F', 'birth_date': '1988-09-18',
            'diagnosis': 'F42 Обсессивно-компульсивное расстройство',
            'mkb_code': 'F42',
            'status': 'DISCHARGED', 
            'doctor': doctors[1] if len(doctors) > 1 else admin,
            'admission_from': 'Поликлиника №7'
        },
        {
            'last_name': 'Лебедев', 'first_name': 'Андрей', 'middle_name': 'Викторович',
            'gender': 'M', 'birth_date': '1955-02-28',
            'diagnosis': 'F60.0 Параноидное расстройство личности',
            'mkb_code': 'F60.0',
            'status': 'HOSPITALIZED', 
            'doctor': doctors[0] if doctors else admin,
            'admission_from': 'Самообращение'
        },
        {
            'last_name': 'Ковалева', 'first_name': 'Наталья', 'middle_name': 'Алексеевна',
            'gender': 'F', 'birth_date': '1999-06-03',
            'diagnosis': 'F43.0 Острая реакция на стресс',
            'mkb_code': 'F43.0',
            'status': 'DISCHARGED', 
            'doctor': doctors[2] if len(doctors) > 2 else admin,
            'admission_from': 'Скорая помощь'
        }
    ]
    
    created_patients = 0
    for i, data in enumerate(patients_data, 1):
        try:
            # Генерируем дату поступления (от 1 до 90 дней назад)
            admission_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            # Проверяем, существует ли уже пациент с таким номером истории
            case_number = f"2024-{i:04d}"
            if Patient.objects.filter(case_number=case_number).exists():
                print(f"  ⚠ Пациент {case_number} уже существует, пропускаем")
                continue
            
            patient = Patient.objects.create(
                case_number=case_number,
                last_name=data['last_name'],
                first_name=data['first_name'],
                middle_name=data['middle_name'],
                gender=data['gender'],
                birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date(),
                address=f'г. Москва, ул. Примерная, д. {i}, кв. {i*2}',
                phone=f'+7 (999) {1000000 + i}',
                admission_date=admission_date,
                admission_from=data['admission_from'],
                admission_diagnosis=data['diagnosis'],
                admission_mkb_code=data['mkb_code'],
                attending_physician=data['doctor'],
                status=data['status'],
                created_by=admin
            )
            
            # Если пациент выписан, добавляем дату выписки и исход
            if data['status'] == 'DISCHARGED':
                discharge_days = random.randint(7, 30)
                patient.discharge_date = admission_date + timedelta(days=discharge_days)
                patient.outcome = random.choice(['RECOVERY', 'IMPROVEMENT', 'NO_CHANGE'])
                patient.work_capacity = random.choice(['RESTORED', 'IMPROVED', 'NO_CHANGE'])
                patient.save()
            
            created_patients += 1
            print(f"  ✓ Пациент {i:2d}: {patient.case_number} - {patient.full_name} ({patient.get_status_display()})")
            
        except Exception as e:
            print(f"  ✗ Ошибка создания пациента {i}: {e}")
    
    print(f"  Всего создано пациентов: {created_patients}")
    
    # 7. Итоговая статистика
    print("\n" + "="*60)
    print("ТЕСТОВЫЕ ДАННЫЕ УСПЕШНО СОЗДАНЫ!")
    print("="*60)
    
    print("\n📊 СТАТИСТИКА:")
    print(f"  • Пользователей: {User.objects.count()}")
    print(f"  • Пациентов: {Patient.objects.count()}")
    print(f"  • Диагнозов: {Diagnosis.objects.count()}")
    
    print("\n🔑 ДОСТУП ДЛЯ ВХОДА:")
    print("  Администратор:")
    print("    Логин: admin")
    print("    Пароль: admin123")
    print("    Роль: Полный доступ")
    
    print("\n  Врачи:")
    print("    Логин: doctor1, doctor2, doctor3")
    print("    Пароль: doctor123")
    print("    Роль: Доступ к своим пациентам")
    
    print("\n  Медсестра:")
    print("    Логин: nurse1")
    print("    Пароль: nurse123")
    print("    Роль: Просмотр всех пациентов")
    
    print("\n  Регистратор:")
    print("    Логин: registrar1")
    print("    Пароль: registrar123")
    print("    Роль: Создание новых пациентов")
    
    print("\n  Аналитик:")
    print("    Логин: analyst1")
    print("    Пароль: analyst123")
    print("    Роль: Просмотр статистики")
    
    print("\n🌐 ДОСТУП К СИСТЕМЕ:")
    print("  • Админ-панель: http://127.0.0.1:8000/admin/")
    print("  • Основное приложение: http://127.0.0.1:8000/")
    
    print("\n⚠  ПРИМЕЧАНИЕ:")
    print("  Для первого входа используйте учетную запись администратора")
    print("  Затем вы можете создавать новых пользователей через админ-панель")
    print("="*60)

if __name__ == '__main__':
    try:
        create_sample_data()
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nКритическая ошибка: {e}")
        print("\nУстранение неполадок:")
        print("1. Убедитесь, что Django установлен: pip install django")
        print("2. Убедитесь, что вы в правильной директории проекта")
        print("3. Проверьте наличие файла manage.py")
        print("4. Примените миграции: python manage.py migrate")
        sys.exit(1)
#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychiatric_clinic.settings')
django.setup()

def load_fixtures():
    """Загружает все фикстуры в правильном порядке"""
    fixtures = [
        'users/fixtures/sample_users.json',
        'patients/fixtures/diagnoses.json',
        'patients/fixtures/sample_patients.json',
        'patients/fixtures/hospitalizations.json'
    ]
    
    for fixture in fixtures:
        print(f"Загрузка {fixture}...")
        try:
            execute_from_command_line(['manage.py', 'loaddata', fixture])
            print(f"✓ {fixture} успешно загружен")
        except Exception as e:
            print(f"✗ Ошибка при загрузке {fixture}: {e}")
            sys.exit(1)
    
    print("\n" + "="*50)
    print("Все фикстуры успешно загружены!")
    print("="*50)
    print("\nДоступные пользователи:")
    print("1. admin / admin123 - Администратор")
    print("2. doctor_sidorova / doctor123 - Врач Сидорова")
    print("3. doctor_kozlov / doctor123 - Врач Козлов")
    print("4. nurse_ivanova / nurse123 - Медсестра Иванова")
    print("5. registrar_smirnov / registrar123 - Регистратор Смирнов")

if __name__ == '__main__':
    load_fixtures()
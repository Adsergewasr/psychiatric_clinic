import os
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from patients.models import Diagnosis


class Command(BaseCommand):
    help = 'Загружает справочник МКБ-10 по психиатрическим заболеваниям'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Путь к JSON файлу с диагнозами',
            default='patients/fixtures/psychiatric_diagnoses_mkb10.json'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            self.stderr.write(f"Файл не найден: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        created = 0
        updated = 0
        
        with transaction.atomic():
            for item in data:
                if item['model'] == 'patients.diagnosis':
                    code = item['fields']['code']
                    name = item['fields']['name']
                    description = item['fields'].get('description', '')
                    
                    obj, created_flag = Diagnosis.objects.update_or_create(
                        code=code,
                        defaults={
                            'name': name,
                            'description': description
                        }
                    )
                    
                    if created_flag:
                        created += 1
                    else:
                        updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Загружено диагнозов: создано {created}, обновлено {updated}'
            )
        )
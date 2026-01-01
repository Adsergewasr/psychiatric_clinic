from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели User"""
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not username:
            raise ValueError(_('Имя пользователя должно быть указано'))
        
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True'))
        
        return self.create_user(username, email, password, **extra_fields)
    
    def get_doctors(self):
        """Получить всех врачей"""
        return self.filter(role='DOCTOR', is_active=True)
    
    def get_nurses(self):
        """Получить всех медсестер"""
        return self.filter(role='NURSE', is_active=True)
    
    def get_active_users(self):
        """Получить всех активных пользователей"""
        return self.filter(is_active=True)
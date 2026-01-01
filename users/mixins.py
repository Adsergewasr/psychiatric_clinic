from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.shortcuts import redirect


class RoleRequiredMixin(AccessMixin):
    """Миксин для проверки роли пользователя"""
    allowed_roles = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if self.allowed_roles is None:
            return super().dispatch(request, *args, **kwargs)
        
        if not isinstance(self.allowed_roles, (list, tuple)):
            self.allowed_roles = [self.allowed_roles]
        
        if request.user.role not in self.allowed_roles:
            return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            from django.contrib import messages
            messages.error(self.request, 'У вас нет прав для выполнения этого действия.')
            return redirect('patients:dashboard')
        return super().handle_no_permission()


class PermissionRequiredMixin(AccessMixin):
    """Миксин для проверки конкретных разрешений"""
    permission_required = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if self.permission_required is None:
            return super().dispatch(request, *args, **kwargs)
        
        if not isinstance(self.permission_required, (list, tuple)):
            self.permission_required = [self.permission_required]
        
        for permission in self.permission_required:
            if not request.user.has_perm(permission):
                return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)


class ObjectPermissionMixin:
    """Миксин для проверки прав на конкретный объект"""
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.has_object_permission(obj):
            raise PermissionDenied("У вас нет прав для доступа к этому объекту.")
        return obj
    
    def has_object_permission(self, obj):
        """Проверка прав на объект"""
        user = self.request.user
        
        # Администраторы имеют доступ ко всему
        if user.is_administrator:
            return True
        
        # Врачи имеют доступ к своим пациентам
        if user.is_doctor:
            if hasattr(obj, 'attending_physician'):
                return obj.attending_physician == user
        
        # Медсестры и регистраторы имеют доступ на чтение ко всему
        if user.is_nurse or user.is_registrar:
            return self.request.method in ['GET', 'HEAD', 'OPTIONS']
        
        # Аналитики имеют доступ только на чтение
        if user.is_analyst:
            return self.request.method in ['GET', 'HEAD', 'OPTIONS']
        
        return False


def role_required(allowed_roles):
    """Декоратор для проверки роли пользователя"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            if not isinstance(allowed_roles, (list, tuple)):
                roles = [allowed_roles]
            else:
                roles = allowed_roles
            
            if request.user.role not in roles:
                from django.contrib import messages
                messages.error(request, 'У вас нет прав для выполнения этого действия.')
                from django.shortcuts import redirect
                return redirect('patients:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def permission_required(perm):
    """Декоратор для проверки конкретного разрешения"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            if not request.user.has_perm(perm):
                from django.contrib import messages
                messages.error(request, 'У вас нет прав для выполнения этого действия.')
                from django.shortcuts import redirect
                return redirect('patients:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
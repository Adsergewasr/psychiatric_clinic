from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings
import logging

from .models import User, UserProfile, LoginHistory
from .forms import (
    CustomAuthenticationForm, UserRegistrationForm, 
    UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm,
    UserSearchForm
)

logger = logging.getLogger(__name__)


def user_login(request):
    """Кастомный вход в систему"""
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    # Логируем вход
                    login_history = LoginHistory.objects.create(
                        user=user,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        success=True
                    )
                    
                    # Обновляем профиль
                    if hasattr(user, 'profile'):
                        user.profile.last_login_ip = login_history.ip_address
                        user.profile.save()
                    
                    # Входим
                    login(request, user)
                    
                    # Настройка сессии
                    if not remember_me:
                        request.session.set_expiry(0)  # Сессия до закрытия браузера
                    
                    # Сообщение об успешном входе
                    messages.success(request, f'Добро пожаловать, {user.get_full_name()}!')
                    
                    # Перенаправление
                    next_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
                    return redirect(next_url)
                else:
                    messages.error(request, 'Учетная запись неактивна')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
        else:
            messages.error(request, 'Ошибка в форме входа')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def user_logout(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect(settings.LOGOUT_REDIRECT_URL)


@login_required
@permission_required('users.can_manage_users', raise_exception=True)
def user_list(request):
    """Список пользователей"""
    form = UserSearchForm(request.GET or None)
    users = User.objects.all().select_related('profile')
    
    # Применяем фильтры
    if form.is_valid():
        query = form.cleaned_data.get('query')
        role = form.cleaned_data.get('role')
        is_active = form.cleaned_data.get('is_active')
        
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone__icontains=query)
            )
        
        if role:
            users = users.filter(role=role)
        
        if is_active == 'true':
            users = users.filter(is_active=True)
        elif is_active == 'false':
            users = users.filter(is_active=False)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'last_name')
    if sort_by.lstrip('-') in ['username', 'last_name', 'first_name', 'role', 'date_joined']:
        users = users.order_by(sort_by)
    
    # Пагинация
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_users': users.count(),
        'sort_by': sort_by,
        'role_stats': {
            'ADMIN': User.objects.filter(role='ADMIN').count(),
            'DOCTOR': User.objects.filter(role='DOCTOR').count(),
            'NURSE': User.objects.filter(role='NURSE').count(),
            'REGISTRAR': User.objects.filter(role='REGISTRAR').count(),
            'ANALYST': User.objects.filter(role='ANALYST').count(),
        }
    }
    
    return render(request, 'users/user_list.html', context)


@login_required
@permission_required('users.can_manage_users', raise_exception=True)
def user_create(request):
    """Создание нового пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            # Отправляем email с паролем (в реальном приложении)
            # send_welcome_email(user, form.cleaned_data['password1'])
            
            messages.success(
                request, 
                f'Пользователь {user.get_full_name()} успешно создан'
            )
            return redirect('users:user_detail', pk=user.pk)
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Создание нового пользователя',
        'submit_text': 'Создать пользователя',
    }
    
    return render(request, 'users/user_form.html', context)


@login_required
def user_detail(request, pk):
    """Просмотр профиля пользователя"""
    user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    
    # Проверка прав доступа
    if not request.user.has_perm('users.can_manage_users'):
        if user != request.user:
            return HttpResponseForbidden('У вас нет прав для просмотра этого профиля')
    
    # Получаем историю входов
    login_history = user.login_history.all()[:10]
    
    context = {
        'user': user,
        'login_history': login_history,
        'can_edit': request.user.has_perm('users.can_manage_users') or user == request.user,
    }
    
    return render(request, 'users/user_detail.html', context)


@login_required
def user_update(request, pk):
    """Редактирование пользователя"""
    user = get_object_or_404(User, pk=pk)
    
    # Проверка прав доступа
    if not request.user.has_perm('users.can_manage_users'):
        if user != request.user:
            return HttpResponseForbidden('У вас нет прав для редактирования этого профиля')
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=user.profile if hasattr(user, 'profile') else None
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('users:user_detail', pk=user.pk)
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(
            instance=user.profile if hasattr(user, 'profile') else None
        )
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
        'title': f'Редактирование пользователя: {user.get_full_name()}',
        'submit_text': 'Сохранить изменения',
    }
    
    return render(request, 'users/user_form.html', context)


@login_required
@permission_required('users.can_manage_users', raise_exception=True)
def user_delete(request, pk):
    """Удаление пользователя"""
    user = get_object_or_404(User, pk=pk)
    
    # Нельзя удалить самого себя
    if user == request.user:
        messages.error(request, 'Вы не можете удалить свою учетную запись')
        return redirect('users:user_detail', pk=user.pk)
    
    if request.method == 'POST':
        user_name = user.get_full_name()
        user.delete()
        messages.success(request, f'Пользователь {user_name} удален')
        return redirect('users:user_list')
    
    context = {
        'user': user,
        'title': 'Подтверждение удаления',
    }
    
    return render(request, 'users/user_confirm_delete.html', context)


@login_required
def profile(request):
    """Профиль текущего пользователя"""
    return redirect('users:user_detail', pk=request.user.pk)


@login_required
def change_password(request):
    """Смена пароля"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен')
            return redirect('users:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': 'Смена пароля',
    }
    
    return render(request, 'users/change_password.html', context)


@login_required
@permission_required('users.can_manage_users', raise_exception=True)
@require_POST
def toggle_user_status(request, pk):
    """Включение/выключение пользователя"""
    user = get_object_or_404(User, pk=pk)
    
    # Нельзя изменить статус самого себя
    if user == request.user:
        return JsonResponse({
            'error': 'Вы не можете изменить статус своей учетной записи'
        }, status=400)
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'активен' if user.is_active else 'неактивен'
    messages.success(request, f'Пользователь {user.get_full_name()} теперь {status}')
    
    return JsonResponse({
        'success': True,
        'is_active': user.is_active,
        'status_text': status
    })


@login_required
def get_doctors(request):
    """API для получения списка врачей"""
    doctors = User.objects.filter(role='DOCTOR', is_active=True)
    
    results = [
        {
            'id': doctor.id,
            'text': doctor.get_full_name(),
            'username': doctor.username,
            'specialization': doctor.specialization or '',
        }
        for doctor in doctors
    ]
    
    return JsonResponse({'results': results})


def get_client_ip(request):
    """Получение IP адреса клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
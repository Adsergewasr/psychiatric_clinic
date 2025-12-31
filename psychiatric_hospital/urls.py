# Первая версия
# from django.contrib import admin
# from django.urls import path, include
# from . import views  # импортируем созданное представление

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('users/', include('users.urls', namespace='users')),
#     path('', views.home_page, name='home'),  # главная страница
# ]

# Вторая версия.
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static

# # Кастомный админ сайт
# admin.site.site_header = 'Психиатрическая больница - Администрация'
# admin.site.site_title = 'Админ-панель психиатрической больницы'
# admin.site.index_title = 'Управление системой'

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('patients.urls')),
#     path('users/', include('users.urls')),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# Кастомный админ сайт
admin.site.site_header = 'Психиатрическая больница - Администрация'
admin.site.site_title = 'Админ-панель психиатрической больницы'
admin.site.index_title = 'Управление системой'

urlpatterns = [
    path('', lambda request: redirect('admin:index'), name='home'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
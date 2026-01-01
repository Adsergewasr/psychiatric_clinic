
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	search_fields = ['username', 'first_name', 'last_name', 'email', 'phone']
	list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
	list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
	ordering = ['username']

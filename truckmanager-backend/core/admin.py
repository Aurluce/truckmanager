from django.contrib import admin
from django.contrib.auth.models import User

# Désenregistrer le modèle User par défaut
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Si vous voulez un admin personnalisé pour User
# from django.contrib.auth.admin import UserAdmin
# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
#     search_fields = ['username', 'email', 'first_name', 'last_name']

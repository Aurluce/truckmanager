# loadings/admin.py
from django.contrib import admin
from .models import Loading

@admin.register(Loading)
class LoadingAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'weight_kg', 'trip', 'is_validated']
    list_filter = ['is_validated', 'created_at']
    search_fields = ['product_name', 'trip__truck__truck_id']
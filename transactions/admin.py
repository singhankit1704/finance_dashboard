from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'category', 'amount', 'date', 'is_deleted')
    list_filter = ('type', 'category', 'is_deleted')
    search_fields = ('description', 'user__username')
    date_hierarchy = 'date'
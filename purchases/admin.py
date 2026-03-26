from django.contrib import admin
from .models import Supplier, PurchaseProcess, PurchaseRequest


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'contact_name', 'email')


@admin.register(PurchaseProcess)
class PurchaseProcessAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_by', 'created_at')
    search_fields = ('title',)
    list_filter = ('status',)


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'quantity', 'requested_by', 'supplier', 'status', 'created_at')
    search_fields = ('product_name',)
    list_filter = ('status',)

from django.contrib import admin
from .models import StockItem, StockMovement


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'product_name', 'category', 'quantity', 'initial_quantity', 'min_stock_level', 'unit', 'supplier')
    search_fields = ('product_code', 'product_name', 'supplier')
    list_filter = ('category', 'unit')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('stock_item', 'movement_type', 'quantity', 'project', 'receiver', 'performer', 'created_at')
    search_fields = ('stock_item__product_name', 'project', 'receiver')
    list_filter = ('movement_type',)

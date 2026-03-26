from django.contrib import admin
from .models import Product, SubPart, ProductSubPart, SubPartMaterial


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('material_code', 'material_name', 'weight', 'standard', 'country')
    search_fields = ('material_code', 'material_name')
    list_filter = ('country',)


@admin.register(SubPart)
class SubPartAdmin(admin.ModelAdmin):
    list_display = ('material_code', 'material_name', 'weight', 'quality')
    search_fields = ('material_code', 'material_name')
    list_filter = ('quality',)


@admin.register(ProductSubPart)
class ProductSubPartAdmin(admin.ModelAdmin):
    list_display = ('product', 'subpart', 'quantity')
    search_fields = ('product__material_name', 'subpart__material_name')


@admin.register(SubPartMaterial)
class SubPartMaterialAdmin(admin.ModelAdmin):
    list_display = ('subpart', 'stock_item', 'unit', 'amount', 'net_weight', 'unit_price')
    search_fields = ('subpart__material_name', 'stock_item__product_name')
    list_filter = ('unit',)

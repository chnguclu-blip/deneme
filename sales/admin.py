from django.contrib import admin
from .models import Customer, SalesOffer, SalesOfferItem, OfferProgress


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'tax_number', 'country', 'created_at')
    search_fields = ('name', 'email', 'tax_number')
    list_filter = ('country',)


class SalesOfferItemInline(admin.TabularInline):
    model = SalesOfferItem
    extra = 0


class OfferProgressInline(admin.TabularInline):
    model = OfferProgress
    extra = 0
    readonly_fields = ('created_at', 'created_by')


@admin.register(SalesOffer)
class SalesOfferAdmin(admin.ModelAdmin):
    list_display = ('offer_number', 'customer', 'project_name', 'status', 'currency', 'offer_date', 'created_by')
    search_fields = ('offer_number', 'customer__name', 'project_name')
    list_filter = ('status', 'currency', 'language')
    inlines = [SalesOfferItemInline, OfferProgressInline]


@admin.register(SalesOfferItem)
class SalesOfferItemAdmin(admin.ModelAdmin):
    list_display = ('offer', 'product_name', 'quantity', 'unit_price')
    search_fields = ('offer__offer_number', 'product_name')


@admin.register(OfferProgress)
class OfferProgressAdmin(admin.ModelAdmin):
    list_display = ('offer', 'status_note', 'created_by', 'created_at')
    search_fields = ('offer__offer_number', 'status_note')

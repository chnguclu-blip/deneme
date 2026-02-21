from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from products.models import Product

class Customer(models.Model):
    name = models.CharField(max_length=255, verbose_name="Müşteri Adı/Unvanı")
    address = models.TextField(verbose_name="Adres", blank=True, null=True)
    phone = models.CharField(max_length=50, verbose_name="Telefon", blank=True, null=True)
    email = models.EmailField(verbose_name="E-Posta", blank=True, null=True)
    tax_number = models.CharField(max_length=50, verbose_name="Vergi No / VKN", blank=True, null=True)     
    country = models.CharField(max_length=100, verbose_name="Ülke", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Müşteri"
        verbose_name_plural = "Müşteriler"
        ordering = ['name']

class SalesOffer(models.Model):
    STATUS_CHOICES = [
        ('WAITING', 'Onay Bekliyor'),
        ('APPROVED', 'Onaylandı'),
        ('REJECTED', 'Reddedildi'),
    ]

    CURRENCY_CHOICES = [
        ('TL', 'Türk Lirası (₺)'),
        ('USD', 'Amerikan Doları ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'Sterlin (£)'),
    ]

    LANGUAGE_CHOICES = [
        ('TR', 'Türkçe'),
        ('EN', 'İngilizce'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="Müşteri", null=True, blank=True)
    description = models.TextField(verbose_name="Açıklama", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WAITING', verbose_name="Durum")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='TL', verbose_name="Para Birimi")
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='TR', verbose_name="Dil")
    
    # --- Offer Settings Fields ---
    # Company Details
    company_name = models.CharField(max_length=255, default='KORUCU MAKİNA', verbose_name="Firma Adı", blank=True)
    company_address = models.TextField(verbose_name="Firma Adresi", blank=True)
    company_tax_office = models.CharField(max_length=100, verbose_name="Vergi Dairesi", blank=True)
    company_tax_number = models.CharField(max_length=50, verbose_name="Vergi No", blank=True)

    # Offer Specifics
    offer_date = models.DateField(default=timezone.now, verbose_name="Teklif Tarihi")
    offer_number = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Teklif No")
    revision_number = models.IntegerField(default=0, verbose_name="Revizyon No")
    pdf_file = models.FileField(upload_to='teklifler/', blank=True, null=True, verbose_name="Teklif PDF")
    
    delivery_place = models.CharField(max_length=255, verbose_name="Teslim Yeri", blank=True)
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Teslim Tarihi")
    validity_date = models.DateField(null=True, blank=True, verbose_name="Geçerlilik Tarihi")
    advance_payment = models.CharField(max_length=255, verbose_name="Avans", blank=True)
    
    terms = models.TextField(verbose_name="Anlaşma Şartları", blank=True)
    notes = models.TextField(verbose_name="Notlar", blank=True)

    # Bank Details
    bank_recipient = models.CharField(max_length=255, verbose_name="Alıcı Adı", blank=True)
    bank_name = models.CharField(max_length=255, verbose_name="Banka Adı", blank=True)
    bank_branch = models.CharField(max_length=255, verbose_name="Şube", blank=True)
    bank_iban = models.CharField(max_length=50, verbose_name="IBAN", blank=True)
    bank_swift = models.CharField(max_length=50, verbose_name="SWIFT No", blank=True)
    payment_method = models.CharField(max_length=255, verbose_name="Ödeme Metodu", blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_offers', verbose_name="Hazırlayan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_offers', verbose_name="Onaylayan")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Onay Tarihi")

    def save(self, *args, **kwargs):
        if not self.offer_number:
            # Generate Offer Number: KRC-{Year}-{Count+1}
            year = datetime.datetime.now().year
            count = SalesOffer.objects.filter(created_at__year=year).count() + 1
            self.offer_number = f"KRC-{year}-{count:04d}"
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def customer_name(self):
        return self.customer.name if self.customer else "Müşteri Seçilmedi"

    def __str__(self):
        return f"{self.customer.name} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Satış Teklifi"
        verbose_name_plural = "Satış Teklifleri"
        ordering = ['-created_at']


class SalesOfferItem(models.Model):
    offer = models.ForeignKey(SalesOffer, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün", null=True, blank=True)
    subpart = models.ForeignKey('products.SubPart', on_delete=models.CASCADE, verbose_name="Alt Parça", null=True, blank=True)
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar", default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Birim Fiyat (TL)", default=0)
    
    # Optional: Snapshot of product name in case it changes
    product_name = models.CharField(max_length=255, verbose_name="Ürün/Parça Adı", blank=True)

    def save(self, *args, **kwargs):
        if not self.product_name:
            if self.product:
                self.product_name = self.product.material_name
            elif self.subpart:
                self.product_name = self.subpart.material_name
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        item_name = self.product.material_name if self.product else (self.subpart.material_name if self.subpart else "Bilinmeyen")
        return f"{self.offer.customer.name} - {item_name}"

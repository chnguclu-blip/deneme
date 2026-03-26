from django.db import models
from django.contrib.auth.models import User

class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name="Firma Adı")
    contact_name = models.CharField(max_length=255, verbose_name="İletişim Kişisi", blank=True, null=True)
    phone = models.CharField(max_length=50, verbose_name="Telefon Numarası", blank=True, null=True)
    email = models.EmailField(verbose_name="E-posta", blank=True, null=True)
    address = models.TextField(verbose_name="Adres", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tedarikçiler"
        verbose_name = "Tedarikçi"


class PurchaseProcess(models.Model):
    STATUS_CHOICES = [
        ('Bekliyor', 'Bekliyor'),
        ('Teklif Alındı', 'Teklif Alındı'),
        ('Onaylandı', 'Onaylandı'),
        ('Sipariş Verildi', 'Sipariş Verildi'),
        ('Teslim Alındı', 'Teslim Alındı'),
        ('İptal Edildi', 'İptal Edildi'),
    ]

    title = models.CharField(max_length=255, verbose_name="Süreç Başlığı")
    description = models.TextField(verbose_name="Açıklama", blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Bekliyor', verbose_name="Durum")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Oluşturan")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

    class Meta:
        verbose_name_plural = "Satın Alma Süreçleri"
        verbose_name = "Satın Alma Süreci"


class PurchaseRequest(models.Model):
    STATUS_CHOICES = [
        ('Talep Edildi', 'Talep Edildi'),
        ('Süreçte', 'Süreçte'),
        ('Tamamlandı', 'Tamamlandı'),
        ('İptal', 'İptal'),
    ]

    product_name = models.CharField(max_length=255, verbose_name="Ürün/Hizmet Adı")
    quantity = models.PositiveIntegerField(verbose_name="Miktar")
    description = models.TextField(verbose_name="Açıklama", blank=True, null=True)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='purchase_requests', verbose_name="Talep Eden")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Önerilen Tedarikçi")
    process = models.ForeignKey(PurchaseProcess, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests', verbose_name="İlgili Süreç")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Talep Edildi', verbose_name="Durum")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} ({self.quantity}) - {self.get_status_display()}"

    class Meta:
        verbose_name_plural = "Satın Alma Talepleri"
        verbose_name = "Satın Alma Talebi"

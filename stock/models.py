from django.db import models

def stock_directory_path(instance, filename):
    return 'dosyalar/stok/{0}/{1}'.format(instance.product_name.strip(), filename)

class StockItem(models.Model):
    CATEGORY_CHOICES = [
        ('HAM MADDE', 'Ham Madde'),
        ('YARI MAMUL', 'Yarı Mamul'),
        ('MAMUL', 'Mamul'),
        ('SARF MALZEME', 'Sarf Malzeme'),
        ('HIRDAVAT', 'Hırdavat'),
    ]

    product_code = models.CharField(max_length=50, verbose_name="Ürün Kodu", blank=True, unique=True)
    product_name = models.CharField(max_length=255, verbose_name="Ürün Adı", db_index=True)
    quality = models.CharField(max_length=100, verbose_name="Kalite", blank=True, null=True)
    waybill_no = models.CharField(max_length=100, verbose_name="İrsaliye No", blank=True, null=True)
    description = models.TextField(verbose_name="Açıklama", blank=True, null=True)
    stock_area = models.CharField(max_length=100, verbose_name="Stok Alanı", blank=True, null=True)
    unit = models.CharField(max_length=50, verbose_name="Birim", default="Adet")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar (Kalan)", default=0)
    initial_quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Giriş Miktarı", default=0)
    min_stock_level = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Kritik Stok Miktarı", default=10)
    
    document = models.FileField(upload_to=stock_directory_path, null=True, blank=True, verbose_name="Dosya (PDF/Resim)")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='HAM MADDE', verbose_name="Kategori")
    sub_category = models.CharField(max_length=50, verbose_name="Alt Kategori", blank=True, null=True)
    
    # New Fields
    unit_weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Birim Ağırlık (kg)", blank=True, null=True)
    shelf_basket = models.CharField(max_length=50, verbose_name="Raf/Sepet No", blank=True, null=True)
    supplier = models.CharField(max_length=100, verbose_name="Tedarikçi", blank=True, null=True)
    lot_no = models.CharField(max_length=50, verbose_name="Lot No", blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, verbose_name="QR Kod")
    
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="İşlemi Yapan")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def used_quantity(self):
        return self.initial_quantity - self.quantity

    def save(self, *args, **kwargs):
        # Auto-generate product_code if not present
        if not self.product_code:
            import time
            import random
            timestamp = int(time.time())
            rand_suffix = random.randint(1000, 9999)
            self.product_code = f"STK-{timestamp}-{rand_suffix}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_code} - {self.product_name}"

    @property
    def is_image(self):
        if self.document:
            name = self.document.name.lower()
            return name.endswith(('.png', '.jpg', '.jpeg'))
        return False

    class Meta:
        verbose_name = "Stok Kalemi"
        verbose_name_plural = "Stok Listesi"
        db_table = 'products_stockitem'


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('IN', 'Giriş'),
        ('OUT', 'Çıkış'),
    ]

    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='movements', verbose_name="Stok Kalemi")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar")
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES, default='OUT', verbose_name="Hareket Tipi")
    
    # Extra info for exit
    project = models.CharField(max_length=255, verbose_name="Kullanılacak Proje", blank=True, null=True)
    receiver = models.CharField(max_length=255, verbose_name="Teslim Alan", blank=True, null=True)
    
    performer = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name="İşlemi Yapan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="İşlem Tarihi")

    def __str__(self):
        return f"{self.movement_type} - {self.stock_item.product_name} - {self.quantity}"

    class Meta:
        verbose_name = "Stok Hareketi"
        verbose_name_plural = "Stok Hareketleri"
        db_table = 'products_stockmovement'

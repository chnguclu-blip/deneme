from django.db import models
import os

# --- Directory Paths ---

def product_directory_path(instance, filename):
    # Unified folder: dosyalar/urunler/<material_name>/<filename>
    return 'dosyalar/urunler/{0}/{1}'.format(instance.material_name.strip(), filename)

def subpart_directory_path(instance, filename):
    # Unified folder: dosyalar/alt_parcalar/<material_name>/<filename>
    return 'dosyalar/alt_parcalar/{0}/{1}'.format(instance.material_name.strip(), filename)

def stock_directory_path(instance, filename):
    # Backward compatibility and unified: dosyalar/stok/<product_name>/<filename>
    # Note: This might be used by migrations even if StockItem is not here.
    # However, for new StockItems, the function in stock/models.py is used.
    # We keep this here strictly for old migrations that reference products.models.stock_directory_path
    if hasattr(instance, 'product_name'):
         return 'dosyalar/stok/{0}/{1}'.format(instance.product_name.strip(), filename)
    return 'dosyalar/stok/unknown/{0}'.format(filename)

# --- Models ---

class Product(models.Model):
    material_code = models.CharField(max_length=50, verbose_name="Malzeme Kodu")
    material_name = models.CharField(max_length=255, verbose_name="Malzeme Adı", db_index=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ağırlığı")
    standard = models.CharField(max_length=100, verbose_name="Standardı")
    country = models.CharField(max_length=100, verbose_name="Ülke")
    attachment = models.FileField(upload_to=product_directory_path, null=True, blank=True, verbose_name="Dosya (PDF/Resim)")

    def __str__(self):
        return f"{self.material_code} - {self.material_name}"

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"


class SubPart(models.Model):
    material_code = models.CharField(max_length=50, verbose_name="Malzeme Kodu")
    material_name = models.CharField(max_length=255, verbose_name="Malzeme Adı", db_index=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Ağırlığı")
    quality = models.CharField(max_length=100, verbose_name="Kalite")
    description = models.TextField(verbose_name="Açıklama", blank=True, null=True)
    quality_doc = models.FileField(upload_to=subpart_directory_path, null=True, blank=True, verbose_name="Kalite Belgesi")
    visual_doc = models.FileField(upload_to=subpart_directory_path, null=True, blank=True, verbose_name="Görsel Dosya")

    def __str__(self):
        return f"{self.material_code} - {self.material_name}"

    class Meta:
        verbose_name = "Alt Parça"
        verbose_name_plural = "Alt Parçalar"

class ProductSubPart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='subparts')
    subpart = models.ForeignKey(SubPart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Adet")

    def __str__(self):
        return f"{self.product.material_name} - {self.subpart.material_name} ({self.quantity})"

    def get_visual_doc_url(self):
        if self.subpart.visual_doc:
            from django.conf import settings
            import os
            from urllib.parse import quote
            
            # Construct the path manually mirroring the upload_to logic
            # This needs to match subpart_directory_path
            subpart_name = self.subpart.material_name.strip()
            filename = os.path.basename(self.subpart.visual_doc.name)
            
            # Since we changed path to dosyalar/alt_parcalar/...
            path = f"dosyalar/alt_parcalar/{subpart_name}/{filename}"
            return f"{settings.MEDIA_URL}{quote(path)}"
        return None


class SubPartMaterial(models.Model):
    subpart = models.ForeignKey(SubPart, on_delete=models.CASCADE, related_name='materials')
    # Use string reference to avoid circular import or loading issues
    stock_item = models.ForeignKey('stock.StockItem', on_delete=models.CASCADE, verbose_name="Stok Malzemesi")
    unit = models.CharField(max_length=50, verbose_name="Birim", default='Adet', choices=[
        ('Adet', 'Adet'), ('Metre', 'Metre'), ('Metrekare', 'Metrekare'), ('Kg', 'Kg')
    ])
    
    amount = models.DecimalField(max_digits=20, decimal_places=10, verbose_name="Miktar", default=0) 
    
    fireli_weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Fireli Ağırlık", null=True, blank=True)
    net_weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Net Ağırlık", null=True, blank=True)
    galvanized_weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Galvanizli Ağırlık", null=True, blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Toplam Ağırlık", null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Birim Fiyat", null=True, blank=True)

    def __str__(self):
        # We can't access stock_item.product_name easily in __str__ if it causes queries, but it's fine
        return f"{self.subpart.material_name} - {self.stock_item.product_name}"

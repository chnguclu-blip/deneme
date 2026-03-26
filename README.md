# KORUCU Makina Takip Otomasyonu (ERP Sistemi)

KORUCU Makina için geliştirilmiş, üretim, stok, satış ve personel süreçlerini tek bir merkezden yönetmeyi sağlayan kapsamlı bir kurumsal kaynak planlama (ERP) projesidir. Sistem **Django** framework'ü ile geliştirilmiş olup veri tabanı olarak **PostgreSQL** kullanmaktadır. Tasarım tarafında ise modern ve hızlı bir arayüz sunmak amacıyla **Tailwind CSS** tercih edilmiştir.

## 🚀 Proje Özellikleri ve Modüller

Proje, temel olarak 4 ana modülden (Django uygulamasından) oluşmaktadır:

### 1. Ürün Yönetimi (`products`)
Ürün ağaçları (BOM - Bill of Materials) ve alt parçaların yönetildiği ana üretim modülü.
* **Ürünler (Products):** Malzeme kodu, adı, ağırlığı ve üretim standartlarının tanımlanması. PDF veya görsel ekleyebilme imkanı.
* **Alt Parçalar (Sub-Parts):** Ürünleri oluşturan alt parçaların (kalite standartları, kalite belgeleri, teknik çizimler ile birlikte) tanımı.
* **Maliyet & Reçete (BOM):** Hangi ürünün, hangi alt parçalardan ve stoklardan ne kadar kullanılarak üretildiğinin (fireli/net/galvanizli ağırlık hesaplamaları ile) takibi.

### 2. Stok Yönetimi (`stock`)
Giren/çıkan tüm ham madde, yarı mamul, sarf malzeme ve hırdavat ürünlerinin takip noktası.
* **Stok Kalemleri:** İrsaliye numarası, parti (lot) numarası, raf/sepet lokasyonu bilgileri ve minimum stok uyarısı.
* **QR Kod Desteği:** Malzemelerin takibini ve yönetimini kolaylaştırmak için otomatik QR kod oluşturabilme.
* **Stok Hareketleri:** Giriş ve çıkış işlemlerinin (hangi projeye, hangi personele teslim edildiğinin) detaylı dökümü.

### 3. Satış ve Teklif Yönetimi (`sales`)
Müşterilere hazırlanacak satış tekliflerinin düzenlendiği ve durumlarının takip edildiği modül.
* **Müşteri Yönetimi:** VKN/Vergi Dairesi, iletişim adresleri gibi müşteri bilgilerinin kayıtlı tutulması.
* **Teklif Oluşturma:** Hazırlanan tekliflerde para birimi (TL, USD, EUR, GBP), dil (TR, EN), geçerlilik süresi, teslim tarihi ve avans detaylarının yönetimi.
* **Revizyon ve PDF:** Geçmiş revizyonların takibi, teklif durumu (Onay Bekliyor, Onaylandı, Reddedildi) ve sisteme otomatik PDF üretim belgelerinin entegrasyonu.

### 4. Kullanıcı Yönetimi (`users`)
Sisteme erişimi olan kullanıcıların rolleri, izinleri ve gruplarının yönetildiği güvenlik katmanı.
* Varsayılan Django yetkilendirme altyapısı özelleştirilerek, modüllere göre farklı yetki gruplandırmaları.

---

## 🛠️ Kurulum Yönergeleri

### Gereksinimler
* Python (3.12+ önerilir)
* PostgreSQL veritabanı
* Git (Versiyon kontrolü)

### 1. Projeyi Klonlama ve Çalışma Ortamını Hazırlama
```bash
git clone https://github.com/chnguclu-blip/deneme.git
cd deneme

# Sanal ortam (Virtual Environment) oluşturma ve aktif etme (Windows için)
python -m venv venv
.\venv\Scripts\activate

# Gerekli kütüphanelerin yüklenmesi (Eğer requirements.txt varsa)
pip install -r requirements.txt
```

### 2. Çevresel Değişkenlerin (Environment Variables) Ayarlanması
Projenin kök dizininde bir `.env` dosyası oluşturun ve aşağıdaki örnek ayarları kendi sunucu/veritabanı bilgilerinize göre doldurun:
```env
DEBUG=True
SECRET_KEY=django-insecure-kisiye-ozel-guvenlik-anahtariniz
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=korucu_erp1
DB_USER=korucu_erp1
DB_PASSWORD=12345
DB_HOST=localhost
DB_PORT=5432
```

### 3. Veritabanı Optimizasyonları ve Taşıma İşlemleri (Migrations)
```bash
# PostgreSQL üzerinde korucu_erp1 veritabanı ve kullanıcısının oluşturulduğundan emin olun.
python manage.py makemigrations
python manage.py migrate
```

### 4. Geliştirme Sunucusunu Başlatma
```bash
python manage.py runserver
```
* Tarayıcınızda `http://127.0.0.1:8000/` adresine giderek siteyi görüntüleyebilirsiniz.
* Süper kullanıcı (Admin) erişimi için `python manage.py createsuperuser` komutunu kullanabilirsiniz.

---

## 💻 Kullanılan Teknolojiler
* **Backend:** Python, Django 6.0
* **Veritabanı:** PostgreSQL
* **Frontend:** Tailwind CSS, HTML5, JavaScript
* **Diğer Entegrasyonlar:** `.env` üzerinden Waitress kullanımı, çevre değişkenleri yönetimi ve otomatik logging (hata yönetimi).

## 🗂️ Dosya Sistemi
Projeye yüklenen dosyalar (görseller, PDF'ler, kalite belgeleri) klasör yapısını kirletmemek adına dinamik yollara aktarılır:
* `dosyalar/urunler/` -> Ürün dökümanları
* `dosyalar/alt_parcalar/` -> Alt parça döküman ve çizimleri
* `dosyalar/stok/` -> Stok giriş irsaliyeleri
* `teklifler/` -> Satış teklifleri

---
*Bu rapor, KORUCU Makina sistemi otomasyonunu geliştirirken takip kolaylığı açısından otomatik olarak güncellenmiştir.*

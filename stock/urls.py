from django.urls import path
from . import views

urlpatterns = [
    path('stok_ekle/', views.stok_ekle, name='stok_ekle'),
    path('delete_stock/<int:pk>/', views.delete_stock, name='delete_stock'),
    path('stok/detay/<int:pk>/', views.stock_detail, name='stock_detail'),
    path('stok/', views.stok_home, name='stok_home'),
    path('stok/goruntule/', views.stok_goruntule, name='stok_goruntule'),
    path('stok/goruntule/<str:product_name>/', views.stok_detay_list, name='stok_detay_list'),
    path('stok/hareket-gecmisi/<int:pk>/', views.get_stock_movements_modal, name='get_stock_movements_modal'),
    path('stok/cikis/', views.stok_cikis, name='stok_cikis'),
    path('stok/cikis/sil/<int:pk>/', views.delete_stock_movement, name='delete_stock_movement'),
    path('stok/cikis/duzenle/<int:pk>/', views.edit_stock_movement, name='edit_stock_movement'),
    path('stok/kritik-guncelle/', views.update_critical_stock, name='update_critical_stock'),
    path('api/check-stock/', views.check_stock_code, name='check_stock_code'),
]

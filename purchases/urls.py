from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    # Supplier
    path('tedarikciler/', views.supplier_list, name='supplier_list'),
    path('tedarikci-ekle/', views.supplier_create, name='supplier_create'),
    path('tedarikci-duzenle/<int:pk>/', views.supplier_edit, name='supplier_edit'),
    path('tedarikci-sil/<int:pk>/', views.supplier_delete, name='supplier_delete'),

    # Process
    path('surecler/', views.process_list, name='process_list'),
    path('surec-ekle/', views.process_create, name='process_create'),
    path('surec-duzenle/<int:pk>/', views.process_edit, name='process_edit'),
    path('surec-sil/<int:pk>/', views.process_delete, name='process_delete'),

    # Request
    path('talepler/', views.request_list, name='request_list'),
    path('talep-ekle/', views.request_create, name='request_create'),
    path('talep-duzenle/<int:pk>/', views.request_edit, name='request_edit'),
    path('talep-sil/<int:pk>/', views.request_delete, name='request_delete'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('urun_ekle/', views.urun_ekle, name='urun_ekle'),
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('alt_parca/', views.alt_parca, name='alt_parca'),
    path('delete_subpart/<int:pk>/', views.delete_subpart, name='delete_subpart'),
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]

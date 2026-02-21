from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_list, name='sales_list'),
    path('create/', views.create_offer, name='create_offer'),
    path('offer/<int:pk>/', views.offer_detail, name='offer_detail'),
    path('offer/<int:pk>/edit/', views.edit_offer, name='edit_offer'),
    path('offer/<int:pk>/approve/', views.approve_offer, name='approve_offer'),
    path('offer/<int:pk>/reject/', views.reject_offer, name='reject_offer'),
    path('offer/<int:pk>/generate-pdf/', views.generate_offer_pdf, name='generate_offer_pdf'),
    path('offer/<int:pk>/letter/', views.offer_letter, name='offer_letter'),
    
    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/edit/<int:pk>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:pk>/', views.delete_customer, name='delete_customer'),
]

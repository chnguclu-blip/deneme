from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_list, name='sales_list'),
    path('create/', views.create_offer, name='create_offer'),
    path('offer/<int:pk>/', views.offer_detail, name='offer_detail'),
    path('offer/<int:pk>/edit/', views.edit_offer, name='edit_offer'),
    path('offer/<int:pk>/approve/', views.approve_offer, name='approve_offer'),
    path('offer/<int:pk>/reject/', views.reject_offer, name='reject_offer'),

    path('offer/<int:pk>/letter/', views.offer_letter, name='offer_letter'),
    path('offer/<int:pk>/send/', views.send_offer, name='send_offer'),
    path('offer/<int:pk>/progress/', views.offer_progress_detail, name='offer_progress_detail'),
    path('offer/<int:pk>/progress/add/', views.add_offer_progress, name='add_offer_progress'),
    path('offer/<int:pk>/set-alarm/', views.set_offer_alarm, name='set_offer_alarm'),
    path('offers/sent/', views.sent_offers_list, name='sent_offers_list'),
    
    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/edit/<int:pk>/', views.edit_customer, name='edit_customer'),
    path('customers/delete/<int:pk>/', views.delete_customer, name='delete_customer'),
]

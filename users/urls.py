from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User URLs
    path('', views.user_list, name='user_list'),
    path('add/', views.add_user, name='add_user'),
    path('edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('delete/<int:pk>/', views.delete_user, name='delete_user'),

    # Group URLs
    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', views.add_group, name='add_group'),
    path('groups/edit/<int:pk>/', views.edit_group, name='edit_group'),
    path('groups/delete/<int:pk>/', views.delete_group, name='delete_group'),
]

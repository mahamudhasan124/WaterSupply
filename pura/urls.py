from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib import admin


urlpatterns = [
    path('',views.landing_page, name='landing'),
    path('', views.home, name='home'),
    path('guideline/',views.guideline, name='guideline'),

    #path('admin',admin.sites.urls, name='admin'),

    path('login/',views.login_page, name='login'),
    path('logout/',views.logout_admin, name='logout'),
    path('register/',views.register_page, name='register'),

    path('customer/', views.customer, name='customer'),
    path('add_customer/', views.add_customer, name='add_customer'),
    path('edit_customer/<str:pk>/', views.edit_customer, name='edit_customer'),
    path('delete_customer/<str:pk>/', views.delete_customer, name= 'delete_customer'),
    path('customer_details/<str:pk>',views.customer_details, name='customer_details'),

    path('staff/', views.staff, name='staff'),
    path('add_staff',views.add_staff, name='add_staff'),
    path('edit_staff/<str:pk>/',views.edit_staff, name='edit_staff'),

    path('delivery/<str:pk>/', views.delivery, name='delivery'),

    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('order/', views.add_order, name='order'),
    path('edit_order/<str:pk>/', views.edit_order, name='edit_order'),
    path('all_order/',views.all_order, name='all_order'),

    path('cost/', views.cost, name='cost'),
    path('edit_cost/<str:pk>/', views.edit_cost, name='edit_cost'),

    path('account/', views.account, name='account'),


]
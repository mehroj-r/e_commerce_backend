from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
    path('init-payme/<int:order_id>/', views.init_payme_payment, name='init_payme'),
    path('status/<str:payment_id>/', views.payment_status, name='payment_status'),
]
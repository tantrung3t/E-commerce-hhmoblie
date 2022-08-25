from django.urls import path, include
from . import views
urlpatterns = [
    path('stripe/webhook/', views.StipeWebhookAPI.as_view()),
    path('stripe/refund/', views.StipeRefundAPI.as_view()),
    path('stripe/checkout/', views.StripeCheckoutAPI.as_view()),
    path('stripe/payment-method/', views.StripePaymentMethodAPI.as_view()),
]
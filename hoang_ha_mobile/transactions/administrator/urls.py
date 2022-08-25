from django.urls import path, include
from . import views

urlpatterns = [
    path('transactions/', views.TransactionAPI.as_view()),
]
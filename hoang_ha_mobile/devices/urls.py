from django.urls import path, include
from . import views
urlpatterns = [
    path('token/', views.DeviceTokenAPI.as_view()),
]
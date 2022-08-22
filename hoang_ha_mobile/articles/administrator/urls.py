from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()

router.register('', ArticleViewSet, basename="articles")

urlpatterns = [
    path('', include(router.urls))
]
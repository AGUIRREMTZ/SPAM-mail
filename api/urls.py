"""
URLs para la API
"""
from django.urls import path
from . import views

urlpatterns = [
    path('predict', views.predict_spam, name='predict_spam'),
    path('health', views.health_check, name='health_check'),
]

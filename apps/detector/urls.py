from django.urls import path
from . import views

app_name = 'detector'

urlpatterns = [
    path('scan/', views.scan_text, name='scan'),
]

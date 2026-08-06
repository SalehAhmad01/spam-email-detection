from django.urls import path
from . import views

app_name = 'inbox'

urlpatterns = [
    path('', views.message_list, name='list'),
    path('submit/', views.submit_message_view, name='submit'),
    path('history/', views.history_view, name='history'),
    path('result/<int:pk>/', views.result_detail_view, name='result'),
    path('bulk-results/', views.bulk_results_view, name='bulk_results'),
]

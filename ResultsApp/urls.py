from django.urls import path
from . import views

urlpatterns = [
    path('add_result/', views.add_result, name='add_result'),
    path('get_students_subjects/', views.get_students_subjects, name='get_students_subjects'),
    
]

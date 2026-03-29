from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),  
    path('student-login/', views.student_login, name='student_login'),
    path('student-register/', views.student_register, name='student_register'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.student_logout, name='student_logout'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('rent-status/', views.rent_status, name='rent_status'),
    path('my-room/', views.my_room, name='my_room'),
    path('facilities/', views.facilities, name='facilities'),
    path('about/', views.about, name='about'),
    path('rooms/', views.room_types, name='room_types'),
    path('contact/', views.contact, name='contact'),
    path('room-preference/', views.room_preference, name='room_preference'),
    
]
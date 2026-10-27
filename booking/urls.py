from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('doctor/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('success/<int:pk>/', views.booking_success, name='booking_success'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('review/add/<int:appointment_pk>/', views.add_review, name='add_review'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('services/', views.services_list, name='services_list'),
    path('doctor/<int:doctor_pk>/review/', views.add_doctor_review, name='add_doctor_review'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('my-reviews/edit/<int:review_pk>/', views.edit_review, name='edit_review'),
    path('my-reviews/delete/<int:review_pk>/', views.delete_review, name='delete_review'),
    path('signup/', views.signup, name='signup'),
]
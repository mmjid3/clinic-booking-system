from django.contrib import admin
from .models import Service, Staff, Appointment

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price')
    search_fields = ('name',)

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    filter_horizontal = ('services',) # Provides a nice dual-list box for selecting services

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'staff', 'service', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'staff', 'service')
    search_fields = ('customer__username', 'staff__name')
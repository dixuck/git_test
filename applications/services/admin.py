from django.contrib import admin

from .models import (
    Service, ServiceHistory, 
    Booking, Patient, 
    Doctor
)

admin.site.register([Service, ServiceHistory, Booking, Patient, Doctor])
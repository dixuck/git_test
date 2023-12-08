from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Booking

@shared_task
def delete_expired_bookings():
    expired_bookings = Booking.objects.filter(date__lt=timezone.now() - timedelta(days=1))
    expired_bookings.delete()

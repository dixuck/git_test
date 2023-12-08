from django.urls import path
from .consumers import DoctorConsumer

websocket_urlpatterns = [
    path('ws/doctors/<int:doctor_id>/', DoctorConsumer.as_asgi()),
]

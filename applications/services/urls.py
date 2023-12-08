from django.urls import path
from rest_framework import routers

from .views import (
    ServiceViewSet, DoctorViewSet, 
    BookingViewSet, PatientViewSet,
    ServiceHistoryListView, ServiceHistoryRetrieveView,
    get_doctor_schedule
)

router = routers.DefaultRouter()
router.register('service', ServiceViewSet, 'services')
router.register('doctor', DoctorViewSet, 'doctors')
router.register('booking', BookingViewSet, 'bookings')
router.register('patient', PatientViewSet, 'patients')
urlpatterns = router.urls + [
    path('serviceHistory/', ServiceHistoryListView.as_view(), name='service-history-list'),
    path('serviceHistory/<int:pk>/', ServiceHistoryRetrieveView.as_view(), name='service-history-detail'),
    path('doctor/<int:doctor_id>/schedule/<str:date>/', get_doctor_schedule, name='doctor_schedule'),

]

from datetime import datetime
from django.http import JsonResponse
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAdminUser, AllowAny, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from permissions import NoOne

from .models import (
    Service, Doctor, Patient,
    Booking, ServiceHistory
)
from .serializers import *


def get_default_permissions(func):
    def wrapper(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser]
        return func(self)
    return wrapper

class ServiceViewSet(ModelViewSet):
    """ POST/PUT/PATCH/DELETE works if user is admin """
    queryset = Service.objects.all() 
    serializer_class = ServiceSerializer
    
    @get_default_permissions
    def get_permissions(self):
        return super().get_permissions()
    
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ServiceDetailSerializer
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    
    
class DoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            self.permission_classes = [AllowAny]
        elif self.request.method in ['POST', 'DELETE']:
            self.permission_classes = [NoOne]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class PatientViewSet(ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_permissions(self):
        self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = PatientDetailSerializer
        return super().retrieve(request, *args, **kwargs)


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    @get_default_permissions
    def get_permissions(self):
        return super().get_permissions() 
    
    @swagger_auto_schema(request_body=SwaggerBookingSerializer)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(request_body=SwaggerBookingSerializer)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(request_body=SwaggerBookingSerializer)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'date',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='date format: YYYY-MM-DD',
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_date(self, request):
        date_param = request.query_params.get('date')  # Получение параметра даты из запроса
        try:
            date = datetime.strptime(date_param, '%Y-%m-%d').date()  # Преобразование строки в объект даты
            bookings = Booking.objects.filter(date=date)  # Запрос для получения всех бронирований на эту дату
            serializer = self.get_serializer(bookings, many=True)
            return Response(serializer.data)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid date format'}, status=400)


class ServiceHistoryListView(ListAPIView):
    queryset = ServiceHistory.objects.all()
    serializer_class = ServiceHistoryListSerializer 

    def get_permissions(self):
        self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    
class ServiceHistoryRetrieveView(RetrieveAPIView):
    queryset = ServiceHistory.objects.all()
    serializer_class = ServiceHistoryRetrieveSerializer 

    def get_permissions(self):
        self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    
@api_view(['GET'])
@swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'doctor_id',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
            description="doctor's ID",
            required=True
        ),
        openapi.Parameter(
            'date',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
            description='date format: YYYY-MM-DD',
            required=True
        )
    ],
    responses={200: DoctorScheduleSerializer(many=True)}
)
def get_doctor_schedule(request, doctor_id, date):
    """ date format: YYYY-MM-DD """
    try:
        doctor = Doctor.objects.get(pk=doctor_id)
        schedule_date = datetime.strptime(date, '%Y-%m-%d').date()
        bookings = Booking.objects.filter(doctor=doctor, date=schedule_date)
        serialized_data = DoctorScheduleSerializer(bookings, many=True)  # Сериализация данных

        return JsonResponse(serialized_data.data, safe=False)
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor does not exist'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    
#TODO количество оказанных услуг, услуги через докторов - доктора через услуги,  написать тесты
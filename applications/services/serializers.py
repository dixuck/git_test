from rest_framework import serializers

from .models import (
    Service, Doctor, Patient,
    Booking, ServiceHistory
)

class DoctorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Doctor
        fields = '__all__'
#TODO representation service for doctor?

class ServiceDetailSerializer(serializers.ModelSerializer):
    doctors = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = '__all__'

    def get_doctors(self, obj):
        doctors = obj.doctor_set.all()
        doctor_serializer = DoctorSerializer(doctors, many=True)
        return doctor_serializer.data


class ServiceSerializer(serializers.ModelSerializer):
    doctors = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = '__all__'

    def get_doctors(self, obj):
        doctors = obj.doctor_set.all()
        doctor_names = [
            {
            'name': doctor.name, 
            'last_name':doctor.last_name
            } 
            for doctor in doctors]
        return doctor_names


class PatientDetailSerializer(serializers.ModelSerializer):
    service_history = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'

    def get_service_history(self, instance):
        service_history = ServiceHistory.objects.filter(patient=instance.pk)
        serializer = ServiceHistoryListSerializer(instance=service_history, many=True)
        return serializer.data


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = '__all__'


class SwaggerBookingSerializer(serializers.Serializer):
    date = serializers.DateField()
    confirmed = serializers.BooleanField()
    patient = serializers.IntegerField()
    doctor = serializers.IntegerField()
    service = serializers.IntegerField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == 'GET':
            fields['doctor'] = DoctorSerializer()
            fields['service'] = ServiceSerializer()
            fields['patient'] = PatientSerializer()
        return fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('request', None).method == 'GET':
            representation['doctor'].pop('services')
            representation['doctor'].pop('schedule')
            representation['doctor'].pop('description')
            representation['service'].pop('doctors')
        return representation


class ServiceHistoryListSerializer(serializers.ModelSerializer):
    service = serializers.CharField(source='service.name')
    doctor = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()
    class Meta:
        model = ServiceHistory
        fields = '__all__'

    def get_doctor(self, obj):
        return {
            'name': obj.doctor.name, 
            'last_name':obj.doctor.last_name
            }
    
    def get_patient(self, obj):
        return {
            'name': obj.patient.name, 
            'last_name':obj.patient.last_name
            }

class ServiceHistoryRetrieveSerializer(serializers.ModelSerializer):
    service = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    patient = PatientSerializer()

    class Meta:
        model = ServiceHistory
        fields = '__all__'

    def get_service(self, obj):
        return {
            'id': obj.service.id,
            'name': obj.service.name,
            'price': obj.service.price,
        }

    def get_doctor(self, obj):
        return {
            'name': obj.doctor.name,
            'last_name': obj.doctor.last_name,
            'phone_number': obj.doctor.phone_number,
            'profession': obj.doctor.profession,
            'description': obj.doctor.description,
            'schedule': obj.doctor.schedule,
        }

class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('id', 'patient', 'service', 'date', 'start_time', 'end_time', 'confirmed')

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


User = get_user_model()
phone_regex = RegexValidator(regex=r'^(\+\d{1,3}|0)\d{10,15}$', 
                            message="Phone number must be entered in the format:" +
                            " '+999999999' or '0999999999'. Up to 15 digits allowed.")

class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self) -> str:
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    # patronymic = models.CharField(max_length=30) # Отчество
    phone_number = models.CharField(validators=[phone_regex], max_length=15)
    profession = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='blank')
    # image = models.ImageField(upload_to='images/avatars/', blank=True, null=True)
    schedule = models.TextField(blank=True, default='blank')
    services = models.ManyToManyField('Service')

    def __str__(self) -> str:
        return self.name


class Patient(models.Model):
    name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(validators=[phone_regex], max_length=15)
    def __str__(self) -> str:
        return self.name


class Booking(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    confirmed = models.BooleanField(default=False)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def clean(self):
        conflicting_bookings = Booking.objects.filter(
            doctor=self.doctor,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk) if self.pk else Booking.objects.filter(
            doctor=self.doctor,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )

        if conflicting_bookings.exists():
            raise ValidationError('Для этого времени уже есть запись.')

        if self.start_time >= self.end_time:
            raise ValidationError('Время начала должно быть раньше времени окончания.')

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f'{self.start_time} - {self.end_time}/ {self.date}'

    class Meta:
        ordering = ['date']



class ServiceHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_DEFAULT, default=None, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_DEFAULT, default=None, null=True)
    service = models.ForeignKey(Service, on_delete=models.SET_DEFAULT, default=None, null=True)
    date = models.DateField()
    confirmed = models.BooleanField()
    start_time = models.TimeField()
    end_time = models.TimeField()

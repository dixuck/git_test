from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Booking, ServiceHistory

@receiver(post_save, sender=Booking)
def create_service_history(sender, instance: Booking, created, **kwargs):
    # Creating service history
    if created:
        ServiceHistory.objects.create(
            patient=instance.patient,
            doctor=instance.doctor,
            service=instance.service,
            date=instance.date,
            confirmed=instance.confirmed,
            start_time = instance.start_time,
            end_time = instance.end_time
            )


@receiver(pre_save, sender=Booking)
def update_service_history(sender, instance: Booking, **kwargs):
    if instance.id is not None:  # Если объект обновлен
        try:
            old_instance = Booking.objects.get(id=instance.id)
        except Booking.DoesNotExist:
            old_instance = None

        if old_instance != instance:
            # Updating service history
            try:
                ServiceHistory.objects.filter(pk=instance.pk).update(
                    patient=instance.patient,
                    doctor=instance.doctor,
                    service=instance.service,
                    date=instance.date,
                    confirmed=instance.confirmed,
                    start_time = instance.start_time,
                    end_time = instance.end_time
                )
            except Exception as e:
                raise Exception('------------------------Booking was not found in history----------------------\nError message: ', e)


@receiver(post_save, sender=Booking)
def notify_doctor(sender, instance: Booking, created, **kwargs):
    if created:
        doctor = instance.doctor
        channel_layer = get_channel_layer()
        start_time = instance.start_time
        end_time = instance.end_time
        patient_info = instance.patient.name + ' ' + instance.patient.last_name
        doctor_name = doctor.name + ' ' + doctor.last_name
        service_name = instance.service.name
        service_price = instance.service.price
        async_to_sync(channel_layer.group_send)(
            f'{doctor.user.pk}',
            {
                "type": "new_booking",
                "message": f"{doctor_name}, you have a new booking with service '{service_name}'\
                from {start_time} to {end_time}, your patient is {patient_info}, price is {service_price}",
            }
        )
    
@receiver(pre_save, sender=Booking)
def update_notify_doctor(sender, instance: Booking, **kwargs):
    if instance.id is not None:
        try:
            old_instance = Booking.objects.get(id=instance.id)
        except Booking.DoesNotExist:
            old_instance = None
    
        doctor = instance.doctor
        channel_layer = get_channel_layer()
        start_time = instance.start_time
        old_start_time = old_instance.start_time
        end_time = instance.end_time
        old_end_time = old_instance.end_time
        old_patient_info = old_instance.patient.name + ' ' + old_instance.patient.last_name
        old_service = old_instance.service.name
        patient_info = instance.patient.name + ' ' + instance.patient.last_name
        doctor_name = doctor.name + ' ' + doctor.last_name
        service_name = instance.service.name
        service_price = instance.service.price
        async_to_sync(channel_layer.group_send)(
            f'{doctor.user.pk}',
            {
                "type": "new_booking",
                "message": f"{doctor_name}, your old booking with service '{old_service}' \
                from {old_start_time} to {old_end_time}, patient {old_patient_info} \
                changed to booking with service '{service_name}'\
                from {start_time} to {end_time}, your patient is {patient_info}, price is {service_price}",
            }
        )
    
@receiver(post_delete, sender=Booking)
def delete_notify_doctor(sender, instance: Booking, **kwargs):
    doctor = instance.doctor
    channel_layer = get_channel_layer()
    start_time = instance.start_time
    end_time = instance.end_time
    patient_info = instance.patient.name + ' ' + instance.patient.last_name
    doctor_name = doctor.name + ' ' + doctor.last_name
    service_name = instance.service.name
    async_to_sync(channel_layer.group_send)(
        f'{doctor.user.pk}',
        {
            "type": "new_booking",
            "message": f"{doctor_name}, your booking with service '{service_name}'\
            from {start_time} to {end_time}, patient is {patient_info} was canceled",
        }
    )
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from reservations.models import Reservation

@receiver(post_save, sender=Reservation)
def notify_restaurant_owner(sender, instance, created, **kwargs):
    if created:
        owner = instance.restaurant.owner
        if owner and owner.groups.filter(name='owner').exists():
            from_email = os.getenv('EMAIL_HOST_USER')
            send_mail(
                subject='Новое бронирование',
                message=(
                    f'В вашем ресторане "{instance.restaurant.name}" '
                    f'создано новое бронирование на {instance.reservation_date}.'
                ),
                from_email=from_email,
                recipient_list=[owner.email],
                fail_silently=True,
            )
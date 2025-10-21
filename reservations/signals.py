import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from reservations.models import Reservation


@receiver(post_save, sender=Reservation)
def notify_restaurant_staff(sender, instance, created, **kwargs):
    if created:
        restaurant = instance.restaurant
        owner = restaurant.owner
        manager = restaurant.manager

        from_email = os.getenv("EMAIL_HOST_USER")
        recipient_list = []

        if owner and owner.groups.filter(name="owner").exists():
            recipient_list.append(owner.email)

        if manager and manager.groups.filter(name="manager").exists():
            recipient_list.append(manager.email)

        recipient_list = list(set(recipient_list))

        message = (
            f'В ресторане "{restaurant.name}" создано новое бронирование.\n'
            f"Имя клиента: {instance.customer_name}\n"
            f"Количество гостей: {instance.number_of_guests}\n"
            f"Дата бронирования: {instance.reservation_date}"
        )

        if recipient_list:
            send_mail(
                subject="Новое бронирование",
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=True,
            )

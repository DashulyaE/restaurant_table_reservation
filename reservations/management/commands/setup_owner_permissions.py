from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Назначает права группе owner"

    def handle(self, *args, **kwargs):
        group_name = "owner"
        permissions_codenames = [
            "can_edit_restaurant",
            "can_delete_restaurant",
            "can_add_restaurant",
            "can_view_table",
            "can_delete_table",
            "can_add_table",
            "can_edit_table",
            "can_change_reservation",
            "can_view_reservations",
            "can_delete_reservations",
        ]

        group, created = Group.objects.get_or_create(name=group_name)

        for codename in permissions_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Право с кодом "{codename}" не найдено.'))

        self.stdout.write(self.style.SUCCESS(f'Права успешно назначены группе "{group_name}".'))

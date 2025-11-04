from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(email="admin@test.ru")
        user.set_password("8888")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        groups = Group.objects.all()
        user.groups.set(groups)

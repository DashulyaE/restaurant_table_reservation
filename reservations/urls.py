from django.urls import path, include
from reservations.apps import ReservationsConfig
from reservations.views import index

app_name = ReservationsConfig.name

urlpatterns = [path("", index)]

from django.conf.urls.static import static
from django.urls import path, include

from config import settings
from reservations.apps import ReservationsConfig
from reservations.views import restaurants_list

app_name = ReservationsConfig.name

urlpatterns = [
    path("", restaurants_list),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
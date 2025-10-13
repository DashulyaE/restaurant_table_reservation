from django.conf.urls.static import static
from django.urls import path, include

from config import settings
from reservations.apps import ReservationsConfig
from reservations.views import restaurants_list, restaurants_detail

app_name = ReservationsConfig.name

urlpatterns = [
    path("", restaurants_list, name='restaurants_list'),
    path("restaurants/<int:pk>/", restaurants_detail, name='restaurants_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
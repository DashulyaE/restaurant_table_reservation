from django.conf.urls.static import static
from django.urls import path, include

from config import settings
from reservations.apps import ReservationsConfig
from reservations.views import RestaurantListView, RestaurantDetailView, RestaurantCreateView, RestaurantUpdateView, \
    RestaurantDeleteView, TableListView, TableDetailView, TableCreateView, TableUpdateView, TableDeleteView

app_name = ReservationsConfig.name

urlpatterns = [
    path("", RestaurantListView.as_view(), name='restaurants_list'),
    path("restaurants/<int:pk>/", RestaurantDetailView.as_view(), name='restaurant_detail'),
    path("restaurants/create", RestaurantCreateView.as_view(), name='restaurant_create'),
    path("restaurants/<int:pk>/update/", RestaurantUpdateView.as_view(), name='restaurant_update'),
    path("restaurants/<int:pk>/delete/", RestaurantDeleteView.as_view(), name='restaurant_delete'),

    path("tables/", TableListView.as_view(), name='table_list'),
    path("tables/<int:pk>/", TableDetailView.as_view(), name='table_detail'),
    path("tables/create", TableCreateView.as_view(), name='table_create'),
    path("tables/<int:pk>/update/", TableUpdateView.as_view(), name='table_update'),
    path("tables/<int:pk>/delete/", TableDeleteView.as_view(), name='table_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
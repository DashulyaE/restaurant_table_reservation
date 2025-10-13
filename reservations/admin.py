from django.contrib import admin
from .models import Restaurant, Table, Reservation


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address")
    search_fields = ("name", "address")


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("id", "number", "restaurant", "size")
    list_filter = ("restaurant",)
    search_fields = ("number",)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "restaurant",
        "table",
        "reservation_date",
        "reservation_start",
        "reservation_and",
        "status",
    )
    list_filter = ("reservation_date", "status")
    search_fields = ("customer_name", "telephone")
    ordering = ("-reservation_date", "-reservation_start")

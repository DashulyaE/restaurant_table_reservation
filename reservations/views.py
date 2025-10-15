from datetime import timedelta, datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from reservations.forms import RestaurantForm, TableForm, ReservationForm, ReservationStatusForm
from reservations.models import Restaurant, Table, Reservation
from reservations.utils import get_date_list, get_time_slots


class RestaurantListView(ListView):
    model = Restaurant


class RestaurantDetailView(DetailView):
    model = Restaurant


class RestaurantCreateView(CreateView):
    model = Restaurant
    form_class = RestaurantForm
    success_url = reverse_lazy("reservations:restaurants_list")


class RestaurantUpdateView(UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    success_url = reverse_lazy("reservations:restaurants_list")

    def get_success_url(self):
        return reverse("reservations:restaurant_detail", args=[self.kwargs.get("pk")])


class RestaurantDeleteView(DeleteView):
    model = Restaurant
    success_url = reverse_lazy("reservations:restaurants_list")
    template_name = "reservations/restaurant_confirm_delete.html"


class TableListView(ListView):
    model = Table


class TableDetailView(DetailView):
    model = Table


class TableCreateView(CreateView):
    model = Table
    form_class = TableForm
    success_url = reverse_lazy("reservations:table_list")


class TableUpdateView(UpdateView):
    model = Table
    form_class = TableForm
    success_url = reverse_lazy("reservations:table_list")

    def get_success_url(self):
        return reverse("reservations:table_detail", args=[self.kwargs.get("pk")])


class TableDeleteView(DeleteView):
    model = Table
    success_url = reverse_lazy("reservations:table_list")
    template_name = "reservations/table_confirm_delete.html"



class ReservationListView(ListView):
    model = Reservation


class ReservationDetailView(DetailView):
    model = Reservation


class ReservationCreateView(CreateView):
    model = Reservation
    form_class = ReservationForm
    success_url = reverse_lazy("reservations:reservation_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передача request, чтобы форма могла получить параметры из GET
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial['reservation_date'] = self.request.GET.get('reservation_date')
        initial['reservation_start'] = self.request.GET.get('reservation_start')
        initial['reservation_and'] = self.request.GET.get('reservation_and')
        restaurant_id = self.request.GET.get('restaurant')
        if restaurant_id:
            try:
                restaurant_obj = Restaurant.objects.get(pk=restaurant_id)
                initial['restaurant'] = restaurant_obj
            except Restaurant.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передача списка ресторанов
        context['restaurants'] = Restaurant.objects.all()

        # Получение параметров из GET-запроса
        restaurant_id = self.request.GET.get('restaurant')
        date = self.request.GET.get('reservation_date')
        start_time = self.request.GET.get('reservation_start')
        end_time = self.request.GET.get('reservation_and')

        # Передача списков для шаблона
        context['date_list'] = get_date_list()
        context['time_slots'] = get_time_slots()

        # Фильтрация столов по выбранным параметрам
        if restaurant_id and date and start_time and end_time:
            tables_qs = Table.objects.filter(restaurant_id=restaurant_id)
            reserved_tables = Reservation.objects.filter(
                restaurant_id=restaurant_id,
                reservation_date=date,
                reservation_and__gt=start_time,
                reservation_start__lt=end_time,
            ).values_list('table_id', flat=True)
            context['available_tables'] = tables_qs.exclude(id__in=reserved_tables)
        elif restaurant_id:
            context['available_tables'] = Table.objects.filter(restaurant_id=restaurant_id)
        else:
            context['available_tables'] = Table.objects.none()

        return context


class ReservationDeleteView(DeleteView):
    model = Reservation
    success_url = reverse_lazy("reservations:reservation_list")
    template_name = "reservations/reservation_confirm_delete.html"


class ReservationUpdateView(UpdateView):
    model = Reservation
    form_class = ReservationStatusForm
    success_url = reverse_lazy("reservations:reservation_list")
    template_name = "reservations/reservation_status_update.html"  # ваш шаблон
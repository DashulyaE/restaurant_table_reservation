from datetime import timedelta, datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from reservations.forms import RestaurantForm, TableForm, ReservationForm
from reservations.models import Restaurant, Table, Reservation


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

from django.shortcuts import get_object_or_404

class ReservationCreateView(CreateView):
    model = Reservation
    form_class = ReservationForm
    success_url = reverse_lazy("reservations:reservation_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["reservation_date"] = self.request.GET.get("reservation_date")
        kwargs["reservation_start"] = self.request.GET.get("reservation_start")
        kwargs["reservation_and"] = self.request.GET.get("reservation_and")
        kwargs["restaurant_id"] = self.request.GET.get("restaurant")
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial["reservation_date"] = self.request.GET.get("reservation_date")
        initial["reservation_start"] = self.request.GET.get("reservation_start")
        initial["reservation_and"] = self.request.GET.get("reservation_and")
        restaurant_id = self.request.GET.get("restaurant")
        if restaurant_id:
            try:
                restaurant_obj = Restaurant.objects.get(pk=restaurant_id)
                initial["restaurant"] = restaurant_obj
            except Restaurant.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant_id = self.request.GET.get("restaurant")
        if restaurant_id:
            restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
            context['restaurant_name'] = restaurant.name
        else:
            context['restaurant_name'] = None
        context['restaurants'] = Restaurant.objects.all()
        return context

# class ReservationCreateView(CreateView):
#     model = Reservation
#     form_class = ReservationForm
#     success_url = reverse_lazy("reservations:reservation_list")
#
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs["reservation_date"] = self.request.GET.get("reservation_date")
#         kwargs["reservation_start"] = self.request.GET.get("reservation_start")
#         kwargs["reservation_and"] = self.request.GET.get("reservation_and")
#         kwargs["restaurant_id"] = self.request.GET.get("restaurant")
#         return kwargs
#
#     def get_initial(self):
#         initial = super().get_initial()
#         initial["reservation_date"] = self.request.GET.get("reservation_date")
#         initial["reservation_start"] = self.request.GET.get("reservation_start")
#         initial["reservation_and"] = self.request.GET.get("reservation_and")
#         initial["restaurant"] = self.request.GET.get("restaurant")
#         return initial


class ReservationDeleteView(DeleteView):
    model = Reservation
    success_url = reverse_lazy("reservations:reservation_list")
    template_name = "reservations/reservation_confirm_delete.html"


class ReservationUpdateView(UpdateView):
    model = Reservation
    form_class = ReservationForm
    success_url = reverse_lazy("reservations:reservation_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Передача restaurant_id для инициализации формы
        if self.object:
            kwargs["restaurant_id"] = self.object.restaurant.pk
        return kwargs

    def get_success_url(self):
        return reverse("reservations:reservation_detail", args=[self.kwargs.get("pk")])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = reverse("reservations:reservation_list")
        if self.object and self.object.restaurant:
            context["selected_restaurant_id"] = self.object.restaurant.pk
        else:
            context["selected_restaurant_id"] = None
        return context

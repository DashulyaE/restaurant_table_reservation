from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from reservations.forms import RestaurantForm, TableForm, ReservationForm, ReservationStatusForm
from reservations.models import Restaurant, Table, Reservation
from reservations.utils import get_date_list, get_time_slots


def contacts(request):
    return render(request, "reservations/contacts.html")


class RestaurantListView(ListView):
    model = Restaurant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["is_owner"] = user.groups.filter(name="owner").exists()
        return context


class RestaurantDetailView(DetailView):
    model = Restaurant


class RestaurantCreateView(CreateView, LoginRequiredMixin):
    permission_required = "reservations.can_add_restaurant"
    model = Restaurant
    form_class = RestaurantForm
    success_url = reverse_lazy("reservations:restaurants_list")

    def form_valid(self, form):
        restaurant = form.save()
        user = self.request.user
        restaurant.owner = user
        restaurant.save()
        return super().form_valid(form)


class RestaurantUpdateView(UpdateView, LoginRequiredMixin):
    permission_required = "reservations.can_edit_restaurant"
    model = Restaurant
    form_class = RestaurantForm
    success_url = reverse_lazy("reservations:restaurants_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if not user.is_superuser and obj.owner != user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse("reservations:restaurant_detail", args=[self.kwargs.get("pk")])


class RestaurantDeleteView(DeleteView, LoginRequiredMixin):
    permission_required = "reservations.can_delete_restaurant"
    model = Restaurant
    success_url = reverse_lazy("reservations:restaurants_list")
    template_name = "reservations/restaurant_confirm_delete.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if not user.is_superuser and obj.owner != user:
            raise PermissionDenied
        return obj


class TableListView(ListView, LoginRequiredMixin):
    model = Table

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        has_permission = user.has_perm("reservations.can_view_table")
        is_owner = user.groups.filter(name="owner").exists()

        if not (has_permission or is_owner):
            return qs.none()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["can_view_table"] = user.is_superuser or user.groups.filter(name__in=["manager", "owner"]).exists()
        return context


class TableDetailView(DetailView):
    model = Table


class TableCreateView(CreateView, LoginRequiredMixin):
    model = Table
    form_class = TableForm
    success_url = reverse_lazy("reservations:table_list")

    def form_valid(self, form):
        table = form.save()
        user = self.request.user
        table.owner = user
        table.save()
        return super().form_valid(form)


class TableUpdateView(UpdateView, LoginRequiredMixin):
    model = Table
    form_class = TableForm
    success_url = reverse_lazy("reservations:table_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if not user.is_superuser and obj.owner != user:
            raise PermissionDenied
        return obj

    def get_success_url(self):
        return reverse("reservations:table_detail", args=[self.kwargs.get("pk")])


class TableDeleteView(DeleteView, LoginRequiredMixin):
    model = Table
    success_url = reverse_lazy("reservations:table_list")
    template_name = "reservations/table_confirm_delete.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if not user.is_superuser and obj.owner != user:
            raise PermissionDenied
        return obj


class ReservationListView(ListView, LoginRequiredMixin):
    model = Reservation

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        for reservation in qs:
            reservation.display_reservation_date = reservation.original_reservation_date
            reservation.display_reservation_start = reservation.original_reservation_start
            reservation.display_reservation_and = reservation.original_reservation_and

        # Если суперюзер — показываем все
        if user.is_superuser:
            return qs

        # Для группы 'user' — фильтр по владельцу
        if user.groups.filter(name="user").exists():
            qs = qs.filter(owner=user)

        if user.groups.filter(name__in=['manager', 'owner']).exists():
            if user.groups.filter(name='manager').exists():
                qs = qs.filter(restaurant__manager=user)
            else:
                qs = qs.filter(restaurant__owner=user)

        return qs


class ReservationDetailView(DetailView):
    model = Reservation


class ReservationCreateView(CreateView, LoginRequiredMixin):
    model = Reservation
    form_class = ReservationForm
    success_url = reverse_lazy("reservations:reservation_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.original_reservation_date = form.instance.reservation_date
        form.instance.original_reservation_start = form.instance.reservation_start
        form.instance.original_reservation_and = form.instance.reservation_and
        table = form.save(commit=False)
        table.owner = self.request.user
        table.save()

        return super().form_valid(form)

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
        context["back_url"] = reverse("reservations:restaurants_list")
        context["restaurants"] = Restaurant.objects.all()

        restaurant_id = self.request.GET.get("restaurant")
        date = self.request.GET.get("reservation_date")
        start_time = self.request.GET.get("reservation_start")
        end_time = self.request.GET.get("reservation_and")

        context["date_list"] = get_date_list()
        context["time_slots"] = get_time_slots()

        if restaurant_id and date and start_time and end_time:
            tables_qs = Table.objects.filter(restaurant_id=restaurant_id)
            reserved_tables = Reservation.objects.filter(
                restaurant_id=restaurant_id,
                reservation_date=date,
                reservation_and__gt=start_time,
                reservation_start__lt=end_time,
            ).values_list("table_id", flat=True)
            context["available_tables"] = tables_qs.exclude(id__in=reserved_tables)
        elif restaurant_id:
            context["available_tables"] = Table.objects.filter(restaurant_id=restaurant_id)
        else:
            context["available_tables"] = Table.objects.none()

        return context


class ReservationDeleteView(DeleteView, LoginRequiredMixin):
    model = Reservation
    success_url = reverse_lazy("reservations:reservation_list")
    template_name = "reservations/reservation_confirm_delete.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if not (user.is_superuser or obj.owner == user or user.groups.filter(name__in=["manager", "owner"]).exists()):
            raise PermissionDenied
        return obj


class ReservationUpdateView(UpdateView, LoginRequiredMixin):
    permission_required = "reservations.can_change_reservation"
    model = Reservation
    form_class = ReservationStatusForm
    success_url = reverse_lazy("reservations:reservation_list")
    template_name = "reservations/reservation_status_update.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if user.groups.filter(name="user").exists() and not user.is_superuser:
            if obj.owner != user:
                raise PermissionDenied
        return obj

    def form_valid(self, form):
        if form.instance.status == "cancelled":
            self.object.reservation_date = None
            self.object.reservation_start = None
            self.object.reservation_and = None
            self.object.save()
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.status == "cancelled":
            for field in form.fields.values():
                field.disabled = True
        return form

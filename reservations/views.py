from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
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
    success_url = reverse_lazy('reservations:restaurants_list')


class RestaurantUpdateView(UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    success_url = reverse_lazy('reservations:restaurants_list')

    def get_success_url(self):
        return reverse('reservations:restaurant_detail', args=[self.kwargs.get('pk')])


class RestaurantDeleteView(DeleteView):
    model = Restaurant
    success_url = reverse_lazy('reservations:restaurants_list')
    template_name = 'reservations/restaurant_confirm_delete.html'


class TableListView(ListView):
    model = Table


class TableDetailView(DetailView):
    model = Table


class TableCreateView(CreateView):
    model = Table
    form_class = TableForm
    success_url = reverse_lazy('reservations:table_list')


class TableUpdateView(UpdateView):
    model = Table
    form_class = TableForm
    success_url = reverse_lazy('reservations:table_list')

    def get_success_url(self):
        return reverse('reservations:table_detail', args=[self.kwargs.get('pk')])


class TableDeleteView(DeleteView):
    model = Table
    success_url = reverse_lazy('reservations:table_list')
    template_name = 'reservations/table_confirm_delete.html'


class ReservationListView(ListView):
    model = Reservation


class ReservationDetailView(DetailView):
    model = Reservation


class ReservationCreateView(CreateView):
    model = Reservation
    form_class = ReservationForm
    success_url = reverse_lazy('reservations:reservation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        restaurant_id = self.request.GET.get('restaurant')
        if restaurant_id:
            kwargs['restaurant_id'] = restaurant_id
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        restaurant_id = self.request.GET.get('restaurant')
        if restaurant_id:
            initial['restaurant'] = restaurant_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant_id = self.request.GET.get('restaurant')
        if not restaurant_id:
            # Если ресторан не выбран, показываем список ресторанов для выбора
            context['show_restaurant_selection'] = True
        else:
            # Если выбран, показываем название ресторана
            try:
                restaurant = Restaurant.objects.get(pk=restaurant_id)
                context['restaurant_name'] = restaurant.name
            except Restaurant.DoesNotExist:
                context['restaurant_name'] = ''
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse('reservations:restaurants_list')
        return context


    def post(self, request, *args, **kwargs):
        if 'select_restaurant' in request.POST:
            restaurant_id = request.POST.get('restaurant')
            if restaurant_id:
                return redirect(f"{request.path}?restaurant={restaurant_id}")
        return super().post(request, *args, **kwargs)

class ReservationDeleteView(DeleteView):
    model = Reservation
    success_url = reverse_lazy('reservations:reservation_list')
    template_name = 'reservations/reservation_confirm_delete.html'


class ReservationUpdateView(UpdateView):
    model = Reservation
    form_class = ReservationForm
    success_url = reverse_lazy('reservations:reservation_list')

    def get_success_url(self):
        return reverse('reservations:reservation_detail', args=[self.kwargs.get('pk')])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse('reservations:reservation_list')
        return context

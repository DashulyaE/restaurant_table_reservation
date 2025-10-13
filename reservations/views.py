from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from reservations.forms import RestaurantForm, TableForm
from reservations.models import Restaurant, Table


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
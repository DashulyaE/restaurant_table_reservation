from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from reservations.forms import RestaurantForm
from reservations.models import Restaurant


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
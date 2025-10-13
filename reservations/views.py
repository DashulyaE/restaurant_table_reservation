from django.shortcuts import render

from reservations.models import Restaurant


def restaurants_list(request):
    restaurants = Restaurant.objects.all()
    context = {"restaurants": restaurants}
    return render(request, "reservations/restaurant_list.html", context)


def restaurants_detail(request, pk):
    restaurant = Restaurant.objects.get(pk=pk)
    context = {"restaurant": restaurant}
    return render(request, "reservations/restaurants_detail.html", context)
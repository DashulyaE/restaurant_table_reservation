from django.shortcuts import render

from reservations.models import Restaurant


def restaurants_list(request):
    restaurants = Restaurant.objects.all()
    context = {"restaurants": restaurants}
    return render(request, "reservations/restaurant_list.html", context)

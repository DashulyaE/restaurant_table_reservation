from django.core.exceptions import ValidationError
from django.forms import ModelForm, BooleanField, ModelChoiceField, Select, ChoiceField

from reservations.models import Restaurant, Table, Reservation
from reservations.utils import get_date_list, get_time_slots


class StyleFormMixin:
    """Класс-миксин для изменения стиля формы"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                existing_style = field.widget.attrs.get("style", "")
                style = f"{existing_style} background-color: #fff;"
                field.widget.attrs["style"] = style


class RestaurantForm(StyleFormMixin, ModelForm):
    """Форма для создания ресторана"""

    class Meta:
        model = Restaurant
        fields = "__all__"


class TableForm(StyleFormMixin, ModelForm):
    """Форма для создания стола"""

    class Meta:
        model = Table
        fields = "__all__"


class ReservationForm(StyleFormMixin, ModelForm):
    reservation_date = ChoiceField(label="Дата", choices=[])
    reservation_start = ChoiceField(label="Время начала", choices=[])
    reservation_and = ChoiceField(label="Время окончания", choices=[])
    table = ModelChoiceField(queryset=Table.objects.none(), label="Стол")

    class Meta:
        model = Reservation
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        reservation_date = kwargs.pop("reservation_date", None)
        reservation_start = kwargs.pop("reservation_start", None)
        reservation_and = kwargs.pop("reservation_and", None)
        restaurant_id = kwargs.pop("restaurant_id", None)
        super().__init__(*args, **kwargs)

        # Заполняем выборы дат и времени
        self.fields["reservation_date"].choices = [(date, date) for date in get_date_list()]
        self.fields["reservation_start"].choices = [(time, time) for time in get_time_slots()]
        self.fields["reservation_and"].choices = [(time, time) for time in get_time_slots()]

        # Устанавливаем queryset для ресторана
        if restaurant_id:
            self.fields["restaurant"].queryset = Restaurant.objects.filter(pk=restaurant_id)
        else:
            self.fields["restaurant"].queryset = Restaurant.objects.all()

        # Фильтруем таблицы по ресторану
        if restaurant_id:
            self.fields["table"].queryset = Table.objects.filter(restaurant_id=restaurant_id)
        else:
            self.fields["table"].queryset = Table.objects.none()

        # Фильтруем по времени, если есть дата и время
        if restaurant_id and reservation_date and reservation_start and reservation_and:
            self.fields["table"].queryset = self.get_available_tables(
                restaurant_id, reservation_date, reservation_start, reservation_and
            )

    def get_available_tables(self, restaurant_id, date, start_time, end_time):
        tables = Table.objects.filter(restaurant_id=restaurant_id)
        reserved_tables = Reservation.objects.filter(
            restaurant_id=restaurant_id,
            reservation_date=date,
            reservation_and__gt=start_time,
            reservation_start__lt=end_time,
        ).values_list("table_id", flat=True)
        return tables.exclude(id__in=reserved_tables)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("reservation_start")
        end_time = cleaned_data.get("reservation_and")
        if start_time and end_time:
            if end_time <= start_time:
                # Добавляем ошибку именно к полю 'reservation_and'
                self.add_error("reservation_and", "Время окончания не должно быть меньше или равно времени начала.")
        return cleaned_data


# class ReservationForm(StyleFormMixin, ModelForm):
#     """Форма для создания резерва стола"""
#
#     restaurant = ModelChoiceField(
#         queryset=Restaurant.objects.all(),
#         required=False,
#         label='Ресторан'
#     )
#
#     class Meta:
#         model = Reservation
#         fields = '__all__'
#
#     def __init__(self, *args, **kwargs):
#         restaurant_id = kwargs.pop('restaurant_id', None)
#         super().__init__(*args, **kwargs)
#
#         # Если есть instance, то поля автоматически заполнятся
#         if self.instance and self.instance.pk:
#             # Устанавливаем queryset для restaurant, если оно не установлено
#             if not self.fields['restaurant'].queryset.exists():
#                 self.fields['restaurant'].queryset = Restaurant.objects.filter(pk=self.instance.restaurant.pk)
#             if self.instance.table:
#                 self.fields['table'].queryset = Table.objects.filter(restaurant=self.instance.restaurant)
#             else:
#                 self.fields['table'].queryset = Table.objects.none()
#
#         elif restaurant_id:
#             self.fields['restaurant'].queryset = Restaurant.objects.filter(pk=restaurant_id)
#             self.fields['restaurant'].disabled = True
#             self.fields['table'].queryset = Table.objects.filter(restaurant_id=restaurant_id)
#         else:
#             self.fields['table'].queryset = Table.objects.none()
#             self.fields['restaurant'].required = True
#
#     def save(self, commit=True):
#         reservation = super().save(commit=False)
#         if 'restaurant' in self.cleaned_data:
#             reservation.restaurant = self.cleaned_data['restaurant']
#         if commit:
#             reservation.save()
#         return reservation

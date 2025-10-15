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
    """Форма для создания резерва стола"""

    reservation_date = ChoiceField(label="Дата", choices=[])
    reservation_start = ChoiceField(label="Время начала", choices=[])
    reservation_and = ChoiceField(label="Время окончания", choices=[])
    table = ModelChoiceField(queryset=Table.objects.none(), label="Стол")
    restaurant = ModelChoiceField(queryset=Restaurant.objects.all(), label="Ресторан")  # добавляем поле

    class Meta:
        model = Reservation
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Заполняем выборы дат и времени
        self.fields["reservation_date"].choices = [(date, date) for date in get_date_list()]
        self.fields["reservation_start"].choices = [(time, time) for time in get_time_slots()]
        self.fields["reservation_and"].choices = [(time, time) for time in get_time_slots()]

        # Устанавливаем queryset для ресторана
        if 'restaurant' in self.data:
            try:
                restaurant_id = int(self.data.get('restaurant'))
                self.fields["restaurant"].queryset = Restaurant.objects.filter(pk=restaurant_id)
                self.fields["restaurant"].initial = restaurant_id
            except (ValueError, TypeError):
                self.fields["restaurant"].queryset = Restaurant.objects.all()
        elif hasattr(self, 'instance') and self.instance.pk:
            self.fields["restaurant"].queryset = Restaurant.objects.filter(pk=self.instance.restaurant.pk)
            self.fields["restaurant"].initial = self.instance.restaurant.pk
        else:
            self.fields["restaurant"].queryset = Restaurant.objects.all()

        # Обновляем список доступных столов
        self.update_available_tables()

    def update_available_tables(self):
        if not self.request:
            return
        data = self.request.GET
        restaurant_id = data.get('restaurant')
        date = data.get('reservation_date')
        start_time = data.get('reservation_start')
        end_time = data.get('reservation_and')

        if restaurant_id and date and start_time and end_time:
            self.fields['table'].queryset = self.get_available_tables(restaurant_id, date, start_time, end_time)
        elif restaurant_id:
            self.fields['table'].queryset = Table.objects.filter(restaurant_id=restaurant_id)
        else:
            self.fields['table'].queryset = Table.objects.none()

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
        start_time_str = cleaned_data.get("reservation_start")
        end_time_str = cleaned_data.get("reservation_and")

        if start_time_str and end_time_str:
            from datetime import datetime
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()

            if end_time <= start_time:
                self.add_error("reservation_and", "Время окончания не должно быть меньше или равно времени начала.")


class ReservationStatusForm(StyleFormMixin, ModelForm):
    """Форма для редактирования статуса резерва"""

    class Meta:
        model = Reservation
        fields = ['status']
from django.forms import ModelForm, BooleanField, ModelChoiceField, Select

from reservations.models import Restaurant, Table, Reservation


class StyleFormMixin:
    """Класс-миксин для изменения стиля формы"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs['class'] = "form-check-input"
            else:
                field.widget.attrs['class'] = "form-control"
                existing_style = field.widget.attrs.get('style', '')
                style = f"{existing_style} background-color: #fff;"
                field.widget.attrs['style'] = style


class RestaurantForm(StyleFormMixin, ModelForm):
    """Форма для создания ресторана"""

    class Meta:
        model = Restaurant
        fields = '__all__'


class TableForm(StyleFormMixin, ModelForm):
    """Форма для создания стола"""

    class Meta:
        model = Table
        fields = '__all__'


class ReservationForm(StyleFormMixin, ModelForm):
    """Форма для создания резерва стола"""

    restaurant = ModelChoiceField(
        queryset=Restaurant.objects.all(),
        required=False,
        label='Ресторан'
    )

    class Meta:
        model = Reservation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        restaurant_id = kwargs.pop('restaurant_id', None)
        super().__init__(*args, **kwargs)

        # Если есть instance, то поля автоматически заполнятся
        if self.instance and self.instance.pk:
            # Устанавливаем queryset для restaurant, если оно не установлено
            if not self.fields['restaurant'].queryset.exists():
                self.fields['restaurant'].queryset = Restaurant.objects.filter(pk=self.instance.restaurant.pk)
            if self.instance.table:
                self.fields['table'].queryset = Table.objects.filter(restaurant=self.instance.restaurant)
            else:
                self.fields['table'].queryset = Table.objects.none()

        elif restaurant_id:
            self.fields['restaurant'].queryset = Restaurant.objects.filter(pk=restaurant_id)
            self.fields['restaurant'].disabled = True
            self.fields['table'].queryset = Table.objects.filter(restaurant_id=restaurant_id)
        else:
            self.fields['table'].queryset = Table.objects.none()
            self.fields['restaurant'].required = True

    def save(self, commit=True):
        reservation = super().save(commit=False)
        if 'restaurant' in self.cleaned_data:
            reservation.restaurant = self.cleaned_data['restaurant']
        if commit:
            reservation.save()
        return reservation

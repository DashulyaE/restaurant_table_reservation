from django.forms import ModelForm, BooleanField, ModelChoiceField, Select

from reservations.models import Restaurant, Table, Reservation


class StyleFormMixin:
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
    class Meta:
        model = Restaurant
        fields = '__all__'


class TableForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Table
        fields = '__all__'


class ReservationForm(StyleFormMixin, ModelForm):
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
        if restaurant_id:
            self.fields['restaurant'].queryset = Restaurant.objects.filter(pk=restaurant_id)
            self.fields['restaurant'].disabled = True
            # Ограничиваем выбор столов
            self.fields['table'].queryset = Table.objects.filter(restaurant_id=restaurant_id)
        else:
            self.fields['table'].queryset = Table.objects.none()
            self.fields['restaurant'].required = True

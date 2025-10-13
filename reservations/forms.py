from django.forms import ModelForm, BooleanField

from reservations.models import Restaurant, Table


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
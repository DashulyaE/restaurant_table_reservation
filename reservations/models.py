from django.db import models


class Restaurant(models.Model):
    """Модель класса ресторан"""

    name = models.CharField(max_length=255, verbose_name="Название ресторана", help_text="Введите название ресторана")
    address = models.CharField(max_length=500, verbose_name="Адрес ресторана", help_text="Введите адрес ресторана")
    contact_info = models.CharField(max_length=255, verbose_name="Телефон ресторана")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание ресторана", help_text="Внесите краткое описание ресторана"
    )
    photo = models.ImageField(
        upload_to="restaurant/photo", verbose_name="Фото ресторана", help_text="Загрузите фото ресторана"
    )
    seating_plan_image = models.ImageField(
        upload_to="seating_plans/photo",
        verbose_name="План рассадки",
        help_text="Загрузите план рассадки",
        default="seating_plans/photo/default.jpg",
    )

    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Table(models.Model):
    """Модель класса стол"""

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="tables",
        verbose_name="Ресторан",
        help_text="Выбрать ресторан",
    )
    number = models.CharField(max_length=50, verbose_name="Номер стола", help_text="Укажите номер стола")
    size = models.PositiveIntegerField(verbose_name="Кол-во мест", help_text="Количество мест за столиком")

    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"
        ordering = ["restaurant", "size"]

    def __str__(self):
        return f"Table {self.number} in {self.restaurant.name}"


class Reservation(models.Model):
    """Модель класса резерв"""

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, verbose_name="Ресторан", related_name="reservations"
    )
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Номер стола", related_name="reservations")
    customer_name = models.CharField(max_length=255, verbose_name="Имя клиента")
    telephone = models.CharField(max_length=255, verbose_name="Телефон клиента")
    number_of_guests = models.PositiveIntegerField(help_text="Количество гостей", verbose_name="Количество гостей")
    reservation_date = models.DateField(help_text="Дата брони", verbose_name="Дата брони", null=True, blank=True)
    reservation_start = models.TimeField(help_text="Время начала брони", verbose_name="Время начала брони", null=True, blank=True)
    reservation_and = models.TimeField(help_text="Время окончания брони", verbose_name="Время окончания брони", null=True, blank=True)
    original_reservation_date = models.DateField(
        verbose_name="Дата бронирования (оригинальная)", null=True, blank=True
    )
    original_reservation_start = models.TimeField(
        verbose_name="Время начала (оригинальное)", null=True, blank=True
    )
    original_reservation_and = models.TimeField(
        verbose_name="Время окончания (оригинальное)", null=True, blank=True
    )
    status_choices = [
        ("confirmed", "Подтверждено"),
        ("cancelled", "Отменено"),
        ("pending", "В ожидании"),
    ]
    status = models.CharField(
        max_length=20, choices=status_choices, default="pending", help_text="Статус брони", verbose_name="Статус брони"
    )

    class Meta:
        verbose_name = "Бронь>"
        verbose_name_plural = "Брони"
        ordering = ["reservation_date", "reservation_start"]

    def __str__(self):
        return f"Резервирование на имя {self.customer_name} стола {self.reservation_date}"

    def save(self, *args, **kwargs):
        if self.status == 'cancelled':
            # сохраняем текущие значения в "оригинальные"
            if not self.original_reservation_date:
                self.original_reservation_date = self.reservation_date
            if not self.original_reservation_start:
                self.original_reservation_start = self.reservation_start
            if not self.original_reservation_and:
                self.original_reservation_and = self.reservation_and
            # обнуляем основные поля
            self.reservation_date = None
            self.reservation_start = None
            self.reservation_and = None
        super().save(*args, **kwargs)

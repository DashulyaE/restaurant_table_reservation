from datetime import datetime, timedelta


def get_date_list():
    """Возвращает список из 7 дат, начиная с сегодняшнего дня"""

    today = datetime.today()
    return [(today + timedelta(days=i)).date().isoformat() for i in range(7)]  # 7 дней


def get_time_slots():
    """Возвращает список временных интервалов в течение дня"""

    times = []
    start_time = datetime.strptime("10:00", "%H:%M")
    end_time = datetime.strptime("22:00", "%H:%M")
    current_time = start_time
    while current_time <= end_time:
        times.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=60)
    return times

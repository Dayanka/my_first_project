from rest_framework import serializers
from .models import Room, Booking

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, data):
        room = data.get('room')
        date_start = data.get('date_start')
        date_end = data.get('date_end')

        # Дополнительная проверка: дата окончания должна быть позже даты начала
        if date_end <= date_start:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")

        # Проверяем, есть ли уже бронирование для этого номера, пересекающееся с указанными датами
        overlapping = Booking.objects.filter(
            room=room,
            date_start__lt=date_end,
            date_end__gt=date_start,
        ).exists()
        if overlapping:
            raise serializers.ValidationError("Номер занят на указанные даты")
        return data


from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Room, Booking
from .serializers import RoomSerializer, BookingSerializer


@api_view(['POST'])
def create_room(request):
    """
    Принимает description и price_per_night.
    Возвращает {"room_id": <id>}.
    """
    description = request.data.get('description')
    price_per_night = request.data.get('price_per_night')
    if not description or not price_per_night:
        return Response({"error": "description and price_per_night are required"},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = RoomSerializer(data={
        "description": description,
        "price_per_night": price_per_night
    })
    if serializer.is_valid():
        room = serializer.save()
        return Response({"room_id": room.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_room(request):
    """
    Принимает room_id.
    Удаляет номер отеля и все связанные бронирования (on_delete=CASCADE).
    """
    room_id = request.data.get('room_id')
    if not room_id:
        return Response({"error": "room_id is required"},
                        status=status.HTTP_400_BAD_REQUEST)

    room = get_object_or_404(Room, pk=room_id)
    room.delete()
    return Response({"message": f"Room {room_id} deleted along with its bookings"},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
def list_rooms(request):
    """
    Возвращает список номеров.
    Если передан room_id, то возвращает только указанную комнату.
    Можно сортировать по price_per_night или created_at,
    задавая ?sort_by=price|date и &order=asc|desc.
    """
    sort_by = request.query_params.get('sort_by')  # 'price' или 'date'
    order = request.query_params.get('order', 'asc')  # 'asc' или 'desc'
    valid_sort_fields = {
        'price': 'price_per_night',
        'date': 'created_at'
    }

    room_id = request.query_params.get('room_id')

    queryset = Room.objects.all()

    # Если передан room_id, фильтруем только по этой комнате
    if room_id:
        queryset = queryset.filter(pk=room_id)

    # Применяем сортировку
    if sort_by in valid_sort_fields:
        field_name = valid_sort_fields[sort_by]
        if order == 'desc':
            field_name = f"-{field_name}"
        queryset = queryset.order_by(field_name)

    # Формируем ответ
    data = []
    for room in queryset:
        data.append({
            "room_id": room.id,
            "description": room.description,
            "price_per_night": str(room.price_per_night),
            "created_at": room.created_at.isoformat()
        })
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_booking(request):
    """
    Принимает room_id, date_start, date_end.
    Возвращает {"booking_id": <id>}.
    """
    room_id = request.data.get('room_id')
    date_start = request.data.get('date_start')
    date_end = request.data.get('date_end')
    if not (room_id and date_start and date_end):
        return Response({"error": "room_id, date_start, date_end are required"},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = BookingSerializer(data={
        "room": room_id,
        "date_start": date_start,
        "date_end": date_end
    })
    if serializer.is_valid():
        booking = serializer.save()
        return Response({"booking_id": booking.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_booking(request):
    """
    Принимает booking_id.
    Удаляет бронирование.
    """
    booking_id = request.data.get('booking_id')
    if not booking_id:
        return Response({"error": "booking_id is required"},
                        status=status.HTTP_400_BAD_REQUEST)

    booking = get_object_or_404(Booking, pk=booking_id)
    booking.delete()
    return Response({"message": f"Booking {booking_id} deleted"},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
def list_bookings(request):
    """
    Если room_id не передан, показываем все бронирования,
    иначе — только бронирования конкретной комнаты.
    """
    room_id = request.query_params.get('room_id')
    queryset = Booking.objects.all().order_by('date_start')

    if room_id:
        queryset = queryset.filter(room_id=room_id)

    data = []
    for b in queryset:
        data.append({
            "booking_id": b.id,
            "date_start": str(b.date_start),
            "date_end": str(b.date_end),
            "room_id": b.room_id
        })
    return Response(data, status=status.HTTP_200_OK)


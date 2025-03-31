from django.urls import path
from .views import (
    create_room,
    delete_room,
    list_rooms,
    create_booking,
    delete_booking,
    list_bookings
)

urlpatterns = [
    # Маршруты для номеров отелей
    path('create', create_room, name='rooms-create'),
    path('delete', delete_room, name='rooms-delete'),
    path('list', list_rooms, name='rooms-list'),

    # Маршруты для бронирований
    path('bookings/create', create_booking, name='bookings-create'),
    path('bookings/delete', delete_booking, name='bookings-delete'),
    path('bookings/list', list_bookings, name='bookings-list'),
]


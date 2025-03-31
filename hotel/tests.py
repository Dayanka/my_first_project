from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Room, Booking

class ExtendedAPITests(APITestCase):
    def setUp(self):
        # Сохраним URL-ы для удобства
        self.room_create_url = reverse('rooms-create')
        self.room_delete_url = reverse('rooms-delete')
        self.room_list_url = reverse('rooms-list')
        self.booking_create_url = reverse('bookings-create')
        self.booking_delete_url = reverse('bookings-delete')
        self.booking_list_url = reverse('bookings-list')

        # Создаем пару номеров для тестов
        response = self.client.post(self.room_create_url, {
            'description': 'Room 1',
            'price_per_night': 100
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.room1_id = response.data.get('room_id')

        response = self.client.post(self.room_create_url, {
            'description': 'Room 2',
            'price_per_night': 150
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.room2_id = response.data.get('room_id')

    def test_create_room(self):
        """Проверка создания номера с обязательными полями."""
        response = self.client.post(self.room_create_url, {
            'description': 'Test Room',
            'price_per_night': 200
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('room_id', response.data)

    def test_delete_room(self):
        """Проверка удаления номера и его отсутствия в списке."""
        # Создаем номер, который затем удалим
        response = self.client.post(self.room_create_url, {
            'description': 'Room to delete',
            'price_per_night': 250
        })
        room_id = response.data.get('room_id')
        # Удаляем номер
        response = self.client.delete(self.room_delete_url, {'room_id': room_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что номер отсутствует в списке
        response = self.client.get(self.room_list_url)
        room_ids = [room['room_id'] for room in response.data]
        self.assertNotIn(room_id, room_ids)

    def test_list_rooms_sorting(self):
        """Проверка сортировки списка номеров по цене."""
        # Создаем еще один номер с более низкой ценой
        response = self.client.post(self.room_create_url, {
            'description': 'Cheaper Room',
            'price_per_night': 50
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Запрашиваем список номеров, сортируя по цене по возрастанию
        list_url = f"{self.room_list_url}?sort_by=price&order=asc"
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(room['price_per_night']) for room in response.data]
        sorted_prices = sorted(prices)
        self.assertEqual(prices, sorted_prices)

    def test_create_booking_success(self):
        """Проверка успешного создания бронирования (даты не пересекаются)."""
        data = {
            'room_id': self.room1_id,
            'date_start': '2022-06-20',
            'date_end': '2022-06-25'
        }
        response = self.client.post(self.booking_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('booking_id', response.data)

    def test_create_booking_overlap(self):
        """Проверка, что бронирование с пересекающимися датами не создается."""
        # Первое бронирование
        data1 = {
            'room_id': self.room1_id,
            'date_start': '2022-06-20',
            'date_end': '2022-06-25'
        }
        response1 = self.client.post(self.booking_create_url, data1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        # Второе бронирование с пересекающимися датами
        data2 = {
            'room_id': self.room1_id,
            'date_start': '2022-06-23',
            'date_end': '2022-06-27'
        }
        response2 = self.client.post(self.booking_create_url, data2)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response2.data)

    def test_delete_booking(self):
        """Проверка удаления бронирования и его отсутствия в списке бронирований."""
        data = {
            'room_id': self.room1_id,
            'date_start': '2022-07-01',
            'date_end': '2022-07-05'
        }
        response = self.client.post(self.booking_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking_id = response.data.get('booking_id')
        # Удаляем бронирование
        response = self.client.delete(self.booking_delete_url, {'booking_id': booking_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что бронирование отсутствует в списке
        list_url = f"{self.booking_list_url}?room_id={self.room1_id}"
        response = self.client.get(list_url)
        booking_ids = [booking['booking_id'] for booking in response.data]
        self.assertNotIn(booking_id, booking_ids)

    def test_list_bookings_ordering(self):
        """Проверка, что список бронирований сортируется по дате начала."""
        data1 = {
            'room_id': self.room1_id,
            'date_start': '2022-08-10',
            'date_end': '2022-08-15'
        }
        data2 = {
            'room_id': self.room1_id,
            'date_start': '2022-08-05',
            'date_end': '2022-08-09'
        }
        response1 = self.client.post(self.booking_create_url, data1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        response2 = self.client.post(self.booking_create_url, data2)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        list_url = f"{self.booking_list_url}?room_id={self.room1_id}"
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dates = [booking['date_start'] for booking in response.data]
        self.assertEqual(dates, sorted(dates))

    def test_booking_date_validation(self):
        """Проверка валидации: дата окончания должна быть позже даты начала."""
        data = {
            'room_id': self.room1_id,
            'date_start': '2022-09-10',
            'date_end': '2022-09-10'  # одинаковые даты
        }
        response = self.client.post(self.booking_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            'room_id': self.room1_id,
            'date_start': '2022-09-15',
            'date_end': '2022-09-10'  # дата окончания раньше даты начала
        }
        response = self.client.post(self.booking_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_booking_missing_fields(self):
        """Проверка ошибки при отсутствии обязательных полей при создании бронирования."""
        data = {
            'room_id': self.room1_id,
            'date_start': '2022-10-10'
            # отсутствует date_end
        }
        response = self.client.post(self.booking_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_room_missing_fields(self):
        """Проверка ошибки при отсутствии обязательных полей при создании номера."""
        response = self.client.post(self.room_create_url, {
            'description': 'Room without price'
            # отсутствует price_per_night
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


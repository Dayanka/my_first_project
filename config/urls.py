from django.http import HttpResponse
from django.urls import path, include
from django.contrib import admin

def index(request):
    return HttpResponse("Добро пожаловать в мой проект!")

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('rooms/', include('hotel.urls')),  # все маршруты из hotel/urls.py будут начинаться с "rooms/"
]


from django.urls import path

from . import views

app_name = "reservations"

urlpatterns = [
    path("", views.my_reservations, name="my"),
    path("yeni/<int:space_pk>/", views.reservation_create, name="create"),
    path("<int:pk>/iptal/", views.reservation_cancel, name="cancel"),
]

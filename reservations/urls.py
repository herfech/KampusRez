from django.urls import path

from . import views

app_name = "reservations"

urlpatterns = [
    path("", views.my_reservations, name="my"),
    path("yeni/<int:space_pk>/", views.reservation_create, name="create"),
    path("<int:pk>/iptal/", views.reservation_cancel, name="cancel"),
    # TR: Personel paneli / ES: Panel del personal
    path("yonetim/", views.manage_panel, name="manage"),
    path("yonetim/<int:pk>/<str:action>/", views.manage_action, name="manage_action"),
]

from django.urls import path

from . import views

app_name = "spaces"

urlpatterns = [
    path("", views.space_list, name="list"),
    path("<int:pk>/", views.space_detail, name="detail"),
    # TR: Alan yönetimi (yönetici) / ES: Gestión de espacios (administrador)
    path("yonetim/", views.manage_list, name="manage"),
    path("yonetim/yeni/", views.manage_create, name="manage_create"),
    path("yonetim/<int:pk>/duzenle/", views.manage_edit, name="manage_edit"),
    path("yonetim/<int:pk>/durum/", views.manage_toggle, name="manage_toggle"),
]

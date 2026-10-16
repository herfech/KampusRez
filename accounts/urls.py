from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("giris/", views.UserLoginView.as_view(), name="login"),
    path("cikis/", views.UserLogoutView.as_view(), name="logout"),
    path("kayit/", views.register, name="register"),
]

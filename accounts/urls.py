from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("giris/", views.UserLoginView.as_view(), name="login"),
    path("cikis/", views.UserLogoutView.as_view(), name="logout"),
    path("kayit/", views.register, name="register"),

    # TR: Profil / ES: Perfil
    path("profil/", views.profile, name="profile"),
    path("profil/duzenle/", views.profile_edit, name="profile_edit"),
    path("parola/degistir/", views.UserPasswordChangeView.as_view(), name="password_change"),

    # TR: Parola sıfırlama / ES: Recuperación de contraseña
    path("parola/sifirla/", views.UserPasswordResetView.as_view(), name="password_reset"),
    path("parola/sifirla/gonderildi/", views.UserPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("parola/sifirla/<uidb64>/<token>/", views.UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("parola/sifirla/tamam/", views.UserPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]

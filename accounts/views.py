"""
TR: Hesap görünümleri: kayıt, giriş/çıkış, profil, parola değiştirme ve parola sıfırlama.
ES: Vistas de cuenta: registro, inicio/cierre de sesión, perfil, cambio y recuperación de contraseña.
"""
from django.contrib import messages
from django.contrib.auth import login, views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from reservations.models import Reservation

from .forms import LoginForm, ProfileForm, RegisterForm


def register(request):
    # TR: Giriş yapmış kullanıcı kayıt sayfasını görmesin
    # ES: Un usuario que ya inició sesión no necesita la página de registro
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Kaydınız tamamlandı. KampüsRez'e hoş geldiniz!")
        return redirect("spaces:list")
    return render(request, "accounts/register.html", {"form": form})


class UserLoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class UserLogoutView(auth_views.LogoutView):
    # TR: Çıkış sadece POST ile yapılır (Django 5 güvenlik kuralı)
    # ES: El cierre de sesión solo se hace por POST (regla de seguridad de Django 5)
    pass


# ----------------------------------------------------------------------
# TR: Profil / ES: Perfil
# ----------------------------------------------------------------------
@login_required
def profile(request):
    """
    TR: Kullanıcının bilgileri, rezervasyon özeti ve son rezervasyonları.
    ES: Datos del usuario, resumen de sus reservas y sus últimas reservas.
    """
    reservations = request.user.reservations.select_related("space")
    now = timezone.now()
    stats = {
        "total": reservations.count(),
        "upcoming": reservations.filter(
            status__in=Reservation.ACTIVE_STATUSES, end_time__gte=now
        ).count(),
        "approved": reservations.filter(status=Reservation.Status.APPROVED).count(),
        "no_show": reservations.filter(no_show=True).count(),
    }
    return render(request, "accounts/profile.html", {
        "stats": stats,
        "recent": reservations.order_by("-start_time")[:5],
    })


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profil bilgileriniz güncellendi.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile_edit.html", {"form": form})


class UserPasswordChangeView(SuccessMessageMixin, auth_views.PasswordChangeView):
    # TR: Giriş yapmış kullanıcı mevcut parolasını girerek yenisini belirler
    # ES: El usuario con sesión iniciada pone su contraseña actual y elige una nueva
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")
    success_message = "Parolanız başarıyla değiştirildi."


# ----------------------------------------------------------------------
# TR: Parola sıfırlama (e-posta ile) — Django'nun hazır, güvenli görünümleri kullanılır.
#     Bağlantıdaki token tek kullanımlıktır ve süresi dolar.
# ES: Recuperación de contraseña (por correo) — se usan las vistas seguras que trae Django.
#     El token del enlace es de un solo uso y caduca.
# ----------------------------------------------------------------------
class UserPasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/emails/password_reset_email.txt"
    subject_template_name = "accounts/emails/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:password_reset_done")


class UserPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class UserPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class UserPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"

"""
TR: Kayıt, giriş ve çıkış görünümleri.
ES: Vistas de registro, inicio y cierre de sesión.
"""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm


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


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    # TR: Çıkış sadece POST ile yapılır (Django 5 güvenlik kuralı)
    # ES: El cierre de sesión solo se hace por POST (regla de seguridad de Django 5)
    pass

"""
TR: Kayıt ve giriş testleri.
ES: Pruebas de registro e inicio de sesión.
"""
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import User


@override_settings(ALLOWED_EMAIL_DOMAINS=["gumushane.edu.tr"])
class RegisterTests(TestCase):
    def data(self, email):
        return {
            "first_name": "Ayşe", "last_name": "Yılmaz", "email": email, "school_number": "2411081500",
            "password1": "GucluSifre.2026", "password2": "GucluSifre.2026",
        }

    def test_institutional_email_registers_as_student(self):
        # TR: Kurumsal e-posta (alt alan adı dahil) kabul edilir ve öğrenci rolü verilir
        # ES: Se acepta el correo institucional (incluido un subdominio) y se asigna el rol de estudiante
        response = self.client.post(reverse("accounts:register"), self.data("Ayse@ogr.gumushane.edu.tr"))
        self.assertRedirects(response, reverse("spaces:list"))
        user = User.objects.get()
        self.assertEqual(user.username, "ayse@ogr.gumushane.edu.tr")
        self.assertEqual(user.role, User.Role.STUDENT)

    def test_external_email_is_rejected(self):
        # TR: Kurum dışı e-posta reddedilir / ES: Se rechaza un correo externo
        response = self.client.post(reverse("accounts:register"), self.data("ayse@gmail.com"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())

    def test_login_with_email(self):
        # TR: E-posta ile giriş yapılabilir / ES: Se puede iniciar sesión con el correo
        User.objects.create_user(username="ali@gumushane.edu.tr", password="GucluSifre.2026")
        response = self.client.post(
            reverse("accounts:login"), {"username": "Ali@gumushane.edu.tr", "password": "GucluSifre.2026"}
        )
        self.assertRedirects(response, reverse("spaces:list"))

    @override_settings(ALLOWED_EMAIL_DOMAINS=[])
    def test_empty_domain_list_accepts_any_email(self):
        # TR: Liste boşsa her e-posta kabul edilir (geliştirme modu)
        # ES: Si la lista está vacía se acepta cualquier correo (modo desarrollo)
        response = self.client.post(reverse("accounts:register"), self.data("ayse@gmail.com"))
        self.assertRedirects(response, reverse("spaces:list"))

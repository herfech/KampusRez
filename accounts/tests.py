"""
TR: Kayıt ve giriş testleri.
ES: Pruebas de registro e inicio de sesión.
"""
import re

from django.core import mail
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

    def test_login_with_mixed_case_username(self):
        # TR: Büyük harfli kullanıcı adı (createsuperuser) ile giriş yapılabilir
        # ES: Se puede entrar con un nombre de usuario con mayúsculas (createsuperuser)
        User.objects.create_superuser(username="KampusRez", email="a@b.com", password="GucluSifre.2026")
        response = self.client.post(
            reverse("accounts:login"), {"username": "KampusRez", "password": "GucluSifre.2026"}
        )
        self.assertRedirects(response, reverse("spaces:list"))


class LanguageTests(TestCase):
    def test_page_is_turkish_even_with_spanish_browser(self):
        # TR: Tarayıcı İspanyolca olsa bile Django'nun hazır metinleri Türkçe gösterilir
        # ES: Aunque el navegador esté en español, los textos propios de Django salen en turco
        response = self.client.get(reverse("accounts:register"), HTTP_ACCEPT_LANGUAGE="es")
        self.assertContains(response, "Parola")
        self.assertNotContains(response, "Contraseña")


class ProfileAndPasswordTests(TestCase):
    """
    TR: Profil, parola değiştirme ve e-posta ile parola sıfırlama testleri.
    ES: Pruebas de perfil, cambio de contraseña y recuperación de contraseña por correo.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="ayse@gumushane.edu.tr", email="ayse@gumushane.edu.tr",
            password="EskiParola.2026", first_name="Ayşe", last_name="Yılmaz",
        )

    def test_profile_requires_login(self):
        url = reverse("accounts:profile")
        self.assertRedirects(self.client.get(url), f"{reverse('accounts:login')}?next={url}")

    def test_profile_shows_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertContains(response, "Ayşe Yılmaz")

    def test_profile_edit(self):
        self.client.force_login(self.user)
        self.client.post(reverse("accounts:profile_edit"), {
            "first_name": "Ayşe", "last_name": "Demir", "school_number": "2411081599",
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, "Demir")
        self.assertEqual(self.user.school_number, "2411081599")

    def test_profile_edit_cannot_change_role(self):
        # TR: Formda olmayan alanlar (rol) gönderilse bile değişmez
        # ES: Aunque se envíen campos que no están en el formulario (rol), no cambian
        self.client.force_login(self.user)
        self.client.post(reverse("accounts:profile_edit"), {
            "first_name": "Ayşe", "last_name": "Yılmaz", "role": "admin",
        })
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, User.Role.STUDENT)

    def test_password_change(self):
        self.client.force_login(self.user)
        self.client.post(reverse("accounts:password_change"), {
            "old_password": "EskiParola.2026",
            "new_password1": "YeniParola.2026", "new_password2": "YeniParola.2026",
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("YeniParola.2026"))

    def test_password_reset_full_flow(self):
        # TR: 1) E-posta iste  2) Bağlantıyı aç  3) Yeni parolayı kaydet  4) Yeni parolayla giriş
        # ES: 1) Pedir el correo  2) Abrir el enlace  3) Guardar la nueva contraseña  4) Entrar con ella
        self.client.post(reverse("accounts:password_reset"), {"email": "ayse@gumushane.edu.tr"})
        self.assertEqual(len(mail.outbox), 1)
        link = re.search(r"https?://[^/]+(/\S+)", mail.outbox[0].body).group(1)

        response = self.client.get(link, follow=True)  # TR: token -> set-password adresine yönlenir
        self.assertContains(response, "Yeni Parola Belirleyin")
        self.client.post(response.redirect_chain[-1][0], {
            "new_password1": "YeniParola.2026", "new_password2": "YeniParola.2026",
        })
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("YeniParola.2026"))

        # TR: Aynı bağlantı ikinci kez kullanılamaz / ES: El mismo enlace no se puede usar dos veces
        response = self.client.get(link, follow=True)
        self.assertContains(response, "Bağlantı geçersiz")

    def test_password_reset_unknown_email_sends_nothing(self):
        # TR: Kayıtlı olmayan e-postaya bir şey gönderilmez ama sayfa aynı mesajı gösterir
        # ES: A un correo no registrado no se envía nada, pero la página muestra el mismo mensaje
        response = self.client.post(reverse("accounts:password_reset"), {"email": "yok@gumushane.edu.tr"})
        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

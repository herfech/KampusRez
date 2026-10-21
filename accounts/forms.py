"""
TR: Kayıt ve giriş formları.
ES: Formularios de registro e inicio de sesión.
"""
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


def is_institutional_email(email):
    """
    TR: E-posta, izin verilen kurumsal alan adlarından birine mi ait? (alt alan adları da kabul edilir)
    ES: ¿El correo pertenece a uno de los dominios institucionales permitidos? (se aceptan subdominios)
    """
    # TR: Liste boşsa kısıtlama yok (geliştirme modu)
    # ES: Si la lista está vacía no hay restricción (modo desarrollo)
    if not settings.ALLOWED_EMAIL_DOMAINS:
        return True
    domain = email.rsplit("@", 1)[-1].lower()
    return any(domain == d or domain.endswith("." + d) for d in settings.ALLOWED_EMAIL_DOMAINS)


class RegisterForm(UserCreationForm):
    """
    TR: Yeni kullanıcı kaydı. Kayıt olan herkes "öğrenci" rolüyle başlar;
        akademik personel ve yönetici rolleri yönetici tarafından verilir.
    ES: Registro de un nuevo usuario. Todos empiezan con el rol "estudiante";
        los roles de personal académico y administrador los asigna el administrador.
    """

    email = forms.EmailField(label="Kurumsal e-posta")
    first_name = forms.CharField(label="Ad", max_length=150)
    last_name = forms.CharField(label="Soyad", max_length=150)
    school_number = forms.CharField(label="Öğrenci / Personel No", max_length=20)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "school_number")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not is_institutional_email(email):
            domains = ", ".join("@" + d for d in settings.ALLOWED_EMAIL_DOMAINS)
            raise forms.ValidationError(f"Lütfen kurumsal e-posta adresinizi kullanın ({domains}).")
        # TR: E-posta aynı zamanda kullanıcı adıdır, bu yüzden benzersiz olmalı
        # ES: El correo también es el nombre de usuario, por eso debe ser único
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta adresiyle zaten bir hesap var.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # TR: Giriş e-posta ile yapılır; kullanıcı adı olarak e-postayı kullanıyoruz
        # ES: Se inicia sesión con el correo; usamos el correo como nombre de usuario
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    # TR: Kullanıcı adı alanını "E-posta" olarak göster
    # ES: Mostrar el campo de usuario como "Correo electrónico"
    username = forms.CharField(label="E-posta", widget=forms.TextInput(attrs={"autofocus": True}))

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()

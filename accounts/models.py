"""
TR: Kullanıcı modeli ve roller.
ES: Modelo de usuario y roles.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    TR: Django'nun hazır kullanıcısını genişletir; rol ve okul numarası ekler.
    ES: Amplía el usuario de Django; añade el rol y el número de estudiante/personal.
    """

    class Role(models.TextChoices):
        # TR: Veritabanında İngilizce değer, arayüzde Türkçe etiket
        # ES: Valor en inglés en la base de datos, etiqueta en turco en la interfaz
        STUDENT = "student", "Öğrenci"
        ACADEMIC = "academic", "Akademik Personel"
        ADMIN = "admin", "Yönetici"

    role = models.CharField("Rol", max_length=20, choices=Role.choices, default=Role.STUDENT)
    school_number = models.CharField("Öğrenci / Personel No", max_length=20, blank=True)

    # TR: Gelmeme (no-show) sayısı ve kısıtlama bitiş tarihi
    # ES: Número de ausencias (no-show) y fecha de fin de la restricción
    no_show_count = models.PositiveIntegerField("Gelmeme sayısı", default=0)
    restricted_until = models.DateTimeField("Kısıtlama bitişi", null=True, blank=True)

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_admin_role(self):
        # TR: Yönetici rolünde mi?
        # ES: ¿Tiene rol de administrador?
        return self.role == self.Role.ADMIN

    @property
    def can_manage_reservations(self):
        """
        TR: Rezervasyon onaylama/reddetme ve gelmeme işaretleme yetkisi (yönetici rolü veya süper kullanıcı).
        ES: Permiso para aprobar/rechazar reservas y marcar ausencias (rol administrador o superusuario).
        """
        return self.is_authenticated and (self.is_admin_role or self.is_superuser)

    @property
    def is_restricted(self):
        # TR: Gelmeme nedeniyle şu an kısıtlı mı? / ES: ¿Está restringido ahora por ausencias?
        return bool(self.restricted_until and self.restricted_until > timezone.now())

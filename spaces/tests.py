"""
TR: Alan yönetimi testleri (yetki, oluşturma, düzenleme, açma/kapama).
ES: Pruebas de la gestión de espacios (permisos, creación, edición, abrir/cerrar).
"""
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from reservations.models import Reservation

from .models import Space


class SpaceManagementTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="ogrenci@gumushane.edu.tr", password="x")
        self.manager = User.objects.create_user(username="idari@gumushane.edu.tr", password="x", role=User.Role.ADMIN)
        self.space = Space.objects.create(
            name="Çalışma Odası A", space_type=Space.SpaceType.STUDY_ROOM, building="Merkez Kütüphane", capacity=6,
        )

    def data(self, **overrides):
        data = {
            "name": "Bilgisayar Lab 3", "space_type": "lab", "building": "Mühendislik Fakültesi", "floor": "2",
            "capacity": "28", "equipment": "28 bilgisayar", "is_active": "on", "requires_approval": "on",
            "max_duration_hours": "2", "weekly_limit": "2", "max_advance_days": "7",
        }
        data.update(overrides)
        return data

    def test_student_gets_403(self):
        # TR: Öğrenci yönetim sayfalarına giremez / ES: Un estudiante no puede entrar en las páginas de gestión
        self.client.force_login(self.student)
        for url in [
            reverse("spaces:manage"),
            reverse("spaces:manage_create"),
            reverse("spaces:manage_edit", args=[self.space.pk]),
        ]:
            self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(reverse("spaces:manage_toggle", args=[self.space.pk])).status_code, 403)

    def test_manager_sees_closed_spaces_too(self):
        Space.objects.create(name="Eski Lab", space_type="lab", building="B Blok", capacity=10, is_active=False)
        self.client.force_login(self.manager)
        response = self.client.get(reverse("spaces:manage"))
        self.assertContains(response, "Eski Lab")
        self.assertContains(response, "Kapalı")

    def test_create_space(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse("spaces:manage_create"), self.data())
        self.assertRedirects(response, reverse("spaces:manage"))
        space = Space.objects.get(name="Bilgisayar Lab 3")
        self.assertTrue(space.requires_approval)
        self.assertEqual(space.capacity, 28)

    def test_duplicate_name_in_same_building_rejected(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse("spaces:manage_create"), self.data(
            name="çalışma odası a", building="Merkez Kütüphane", space_type="study_room",
        ))
        self.assertContains(response, "aynı isimde bir alan zaten var")
        self.assertEqual(Space.objects.count(), 1)

    def test_duplicate_check_handles_turkish_letters(self):
        # TR: "İ/i" ve "Ş/ş" farkı aynı isim sayılır / ES: "İ/i" y "Ş/ş" cuentan como el mismo nombre
        Space.objects.create(name="İŞLETME LAB", space_type="lab", building="İktisat", capacity=20)
        self.client.force_login(self.manager)
        response = self.client.post(reverse("spaces:manage_create"), self.data(name="işletme lab", building="iktisat"))
        self.assertContains(response, "aynı isimde bir alan zaten var")
        # TR: "IŞIK" ile "ışık" aynı, "Işık" ile "İşik" farklıdır / ES: "IŞIK" y "ışık" son iguales; "Işık" e "İşik" no
        Space.objects.create(name="IŞIK SALONU", space_type="study_room", building="A Blok", capacity=10)
        response = self.client.post(reverse("spaces:manage_create"), self.data(name="ışık salonu", building="A Blok"))
        self.assertContains(response, "aynı isimde bir alan zaten var")

    def test_invalid_values_rejected(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse("spaces:manage_create"), self.data(capacity="0", max_duration_hours="20"))
        self.assertContains(response, "Kapasite en az 1")
        self.assertContains(response, "1 ile 12 saat")
        self.assertFalse(Space.objects.filter(name="Bilgisayar Lab 3").exists())

    def test_edit_space(self):
        self.client.force_login(self.manager)
        self.client.post(reverse("spaces:manage_edit", args=[self.space.pk]), self.data(
            name="Çalışma Odası A", space_type="study_room", building="Merkez Kütüphane",
            capacity="10", requires_approval="",
        ))
        self.space.refresh_from_db()
        self.assertEqual(self.space.capacity, 10)
        self.assertFalse(self.space.requires_approval)

    def test_toggle_closes_and_hides_from_students(self):
        # TR: Kapatılan alan öğrenci listesinde görünmez, silinmez
        # ES: Un espacio cerrado no aparece en la lista del estudiante, pero no se borra
        self.client.force_login(self.manager)
        self.client.post(reverse("spaces:manage_toggle", args=[self.space.pk]))
        self.space.refresh_from_db()
        self.assertFalse(self.space.is_active)

        self.client.force_login(self.student)
        self.assertNotIn(self.space, self.client.get(reverse("spaces:list")).context["spaces"])
        self.assertEqual(self.client.get(reverse("spaces:detail", args=[self.space.pk])).status_code, 404)

    def test_closing_warns_about_upcoming_reservations(self):
        start = timezone.now() + timedelta(days=1)
        Reservation.objects.create(
            user=self.student, space=self.space, start_time=start, end_time=start + timedelta(hours=1),
            status=Reservation.Status.APPROVED,
        )
        self.client.force_login(self.manager)
        response = self.client.post(reverse("spaces:manage_toggle", args=[self.space.pk]), follow=True)
        self.assertContains(response, "1 yaklaşan rezervasyon")
        self.assertEqual(Reservation.objects.count(), 1)  # TR: Rezervasyon silinmez / ES: La reserva no se borra

    def test_toggle_requires_post(self):
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get(reverse("spaces:manage_toggle", args=[self.space.pk])).status_code, 405)

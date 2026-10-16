"""
TR: Rezervasyon kurallarının testleri. Çalıştırmak için: python manage.py test
ES: Pruebas de las reglas de reserva. Para ejecutarlas: python manage.py test
"""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from spaces.models import Space

from .models import Reservation


class ReservationRuleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ogrenci1", password="test12345")
        self.other = User.objects.create_user(username="ogrenci2", password="test12345")
        self.study_room = Space.objects.create(
            name="Çalışma Odası 1", space_type=Space.SpaceType.STUDY_ROOM,
            building="Merkez Kütüphane", capacity=6,
        )
        self.lab = Space.objects.create(
            name="Bilgisayar Lab 1", space_type=Space.SpaceType.LAB,
            building="Mühendislik", capacity=30, requires_approval=True,
        )
        # TR: Yarın saat 10:00 / ES: Mañana a las 10:00
        self.start = (timezone.localtime() + timedelta(days=1)).replace(
            hour=10, minute=0, second=0, microsecond=0
        )

    def make(self, space=None, user=None, start=None, hours=1):
        start = start or self.start
        return Reservation(
            user=user or self.user, space=space or self.study_room,
            start_time=start, end_time=start + timedelta(hours=hours),
        )

    def save_valid(self, reservation):
        reservation.full_clean()
        reservation.save()
        return reservation

    def test_study_room_is_auto_approved(self):
        # TR: Onay gerektirmeyen alan anında onaylanır / ES: Espacio sin aprobación se aprueba al instante
        r = self.save_valid(self.make())
        self.assertEqual(r.status, Reservation.Status.APPROVED)

    def test_lab_waits_for_approval(self):
        # TR: Laboratuvar rezervasyonu beklemede kalır / ES: La reserva de laboratorio queda pendiente
        r = self.save_valid(self.make(space=self.lab))
        self.assertEqual(r.status, Reservation.Status.PENDING)

    def test_overlapping_reservation_is_rejected(self):
        # TR: Aynı alanda kesişen saatler reddedilir / ES: Se rechaza un horario que se solapa en el mismo espacio
        self.save_valid(self.make())
        overlapping = self.make(user=self.other, start=self.start + timedelta(minutes=30))
        with self.assertRaises(ValidationError):
            overlapping.full_clean()

    def test_back_to_back_reservations_are_allowed(self):
        # TR: Biri bitince diğeri başlayabilir / ES: Una puede empezar justo cuando termina la otra
        self.save_valid(self.make())
        self.save_valid(self.make(user=self.other, start=self.start + timedelta(hours=1)))

    def test_cancelled_reservation_frees_the_slot(self):
        # TR: İptal edilen rezervasyon alanı boşaltır / ES: Una reserva cancelada libera el horario
        r = self.save_valid(self.make())
        r.status = Reservation.Status.CANCELLED
        r.save()
        self.save_valid(self.make(user=self.other))

    def test_max_duration(self):
        # TR: Varsayılan sınır 2 saattir / ES: El límite por defecto es de 2 horas
        with self.assertRaises(ValidationError):
            self.make(hours=3).full_clean()

    def test_past_date_is_rejected(self):
        # TR: Geçmiş tarih reddedilir / ES: Se rechaza una fecha pasada
        with self.assertRaises(ValidationError):
            self.make(start=self.start - timedelta(days=2)).full_clean()

    def test_max_advance_days(self):
        # TR: 7 günden fazla önceden rezervasyon yapılamaz / ES: No se puede reservar con más de 7 días de antelación
        with self.assertRaises(ValidationError):
            self.make(start=self.start + timedelta(days=10)).full_clean()

    def test_weekly_limit(self):
        # TR: Aynı hafta içinde 4. rezervasyon reddedilir (sınır 3)
        # ES: Se rechaza la 4.ª reserva de la misma semana (límite 3)
        monday = self.start + timedelta(days=7 - self.start.weekday())  # TR: gelecek pazartesi / ES: próximo lunes
        self.study_room.max_advance_days = 14
        self.study_room.save()
        for i in range(3):
            self.save_valid(self.make(start=monday + timedelta(hours=2 * i)))
        with self.assertRaises(ValidationError):
            self.make(start=monday + timedelta(hours=8)).full_clean()

    def test_restricted_user_cannot_reserve(self):
        # TR: Kısıtlanan kullanıcı rezervasyon yapamaz / ES: Un usuario restringido no puede reservar
        self.user.restricted_until = timezone.now() + timedelta(days=3)
        self.user.save()
        with self.assertRaises(ValidationError):
            self.make().full_clean()

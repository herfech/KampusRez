"""
TR: Rezervasyon oluşturma ve düzenleme formu.
ES: Formulario para crear y editar una reserva.
"""
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Reservation


class ReservationForm(forms.Form):
    """
    TR: Kullanıcı tarih, başlangıç ve bitiş saatini ayrı seçer; form bunları birleştirir.
        Kural kontrollerinin tamamı modeldeki clean() metodunda yapılır.
        "reservation" verilirse form düzenleme modunda çalışır.
    ES: El usuario elige fecha, hora de inicio y hora de fin por separado; el formulario las une.
        Todas las reglas se comprueban en el método clean() del modelo.
        Si se pasa "reservation", el formulario funciona en modo edición.
    """

    date = forms.DateField(label="Tarih", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    start = forms.TimeField(label="Başlangıç saati", widget=forms.TimeInput(attrs={"type": "time", "step": 900}, format="%H:%M"))
    end = forms.TimeField(label="Bitiş saati", widget=forms.TimeInput(attrs={"type": "time", "step": 900}, format="%H:%M"))
    purpose = forms.CharField(
        label="Amaç", max_length=200, required=False,
        widget=forms.TextInput(attrs={"placeholder": "Örn. grup çalışması, telafi dersi"}),
    )

    def __init__(self, *args, user, space, reservation=None, **kwargs):
        self.user = user
        self.space = space
        self.reservation = reservation  # TR: Düzenlenen kayıt (varsa) / ES: Reserva que se edita (si hay)
        self.instance = None
        self.needs_reapproval = False

        # TR: Düzenleme modunda mevcut değerlerle doldur / ES: En modo edición, rellenar con los valores actuales
        if reservation and "initial" not in kwargs:
            start = timezone.localtime(reservation.start_time)
            end = timezone.localtime(reservation.end_time)
            kwargs["initial"] = {
                "date": start.date(), "start": start.time(), "end": end.time(), "purpose": reservation.purpose,
            }
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        date, start, end = cleaned.get("date"), cleaned.get("start"), cleaned.get("end")
        if not (date and start and end):
            return cleaned

        # TR: Tarih ve saati İstanbul saat dilimine göre birleştir
        # ES: Unir fecha y hora según la zona horaria de Estambul
        start_time = timezone.make_aware(datetime.combine(date, start))
        end_time = timezone.make_aware(datetime.combine(date, end))

        if self.reservation:
            # TR: Düzenleme: mevcut kaydı güncelle. Saat değiştiyse kurallar yeni kayıt gibi kontrol edilir.
            # ES: Edición: se actualiza la reserva existente. Si cambió el horario, las reglas se
            #     comprueban como si fuera nueva.
            reservation = self.reservation
            rescheduled = (reservation.start_time != start_time or reservation.end_time != end_time)
            reservation._rescheduled = rescheduled
            # TR: Onay gerektiren alanda saati değişen onaylı rezervasyon yeniden onaya düşer
            # ES: En espacios con aprobación, una reserva aprobada a la que se le cambia la hora vuelve a pendiente
            if rescheduled and self.space.requires_approval and reservation.status == Reservation.Status.APPROVED:
                reservation.status = Reservation.Status.PENDING
                self.needs_reapproval = True
        else:
            reservation = Reservation(user=self.user, space=self.space)

        reservation.start_time = start_time
        reservation.end_time = end_time
        reservation.purpose = cleaned.get("purpose", "")

        try:
            reservation.full_clean()
        except ValidationError as exc:
            # TR: Modelden gelen hataları formun genel hatası olarak göster
            # ES: Mostrar los errores del modelo como errores generales del formulario
            for message in exc.messages:
                self.add_error(None, message)
        else:
            self.instance = reservation
        return cleaned

    def save(self):
        self.instance.save()
        return self.instance

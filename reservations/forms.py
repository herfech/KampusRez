"""
TR: Rezervasyon oluşturma formu.
ES: Formulario para crear una reserva.
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
    ES: El usuario elige fecha, hora de inicio y hora de fin por separado; el formulario las une.
        Todas las reglas se comprueban en el método clean() del modelo.
    """

    date = forms.DateField(label="Tarih", widget=forms.DateInput(attrs={"type": "date"}))
    start = forms.TimeField(label="Başlangıç saati", widget=forms.TimeInput(attrs={"type": "time", "step": 900}))
    end = forms.TimeField(label="Bitiş saati", widget=forms.TimeInput(attrs={"type": "time", "step": 900}))
    purpose = forms.CharField(
        label="Amaç", max_length=200, required=False,
        widget=forms.TextInput(attrs={"placeholder": "Örn. grup çalışması, telafi dersi"}),
    )

    def __init__(self, *args, user, space, **kwargs):
        self.user = user
        self.space = space
        self.instance = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        date, start, end = cleaned.get("date"), cleaned.get("start"), cleaned.get("end")
        if not (date and start and end):
            return cleaned

        # TR: Tarih ve saati İstanbul saat dilimine göre birleştir
        # ES: Unir fecha y hora según la zona horaria de Estambul
        reservation = Reservation(
            user=self.user,
            space=self.space,
            start_time=timezone.make_aware(datetime.combine(date, start)),
            end_time=timezone.make_aware(datetime.combine(date, end)),
            purpose=cleaned.get("purpose", ""),
        )
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

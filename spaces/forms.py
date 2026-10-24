"""
TR: Alan oluşturma ve düzenleme formu (yönetici).
ES: Formulario para crear y editar espacios (administrador).
"""
from django import forms

from .models import Space


class SpaceForm(forms.ModelForm):
    class Meta:
        model = Space
        fields = (
            "name", "space_type", "building", "floor", "capacity", "equipment", "is_active",
            "requires_approval", "max_duration_hours", "weekly_limit", "max_advance_days",
        )
        widgets = {
            "equipment": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "requires_approval": "İşaretlenirse rezervasyonlar personel onayıyla kesinleşir (ör. laboratuvarlar).",
            "max_duration_hours": "Tek bir rezervasyonun en fazla kaç saat sürebileceği.",
            "weekly_limit": "Bir kullanıcının bu alan için haftada yapabileceği en fazla rezervasyon sayısı.",
            "max_advance_days": "Kaç gün öncesine kadar rezervasyon yapılabileceği.",
        }

    # TR: Mantıksız değerleri engelle / ES: Impedir valores sin sentido
    def clean_capacity(self):
        value = self.cleaned_data["capacity"]
        if value < 1:
            raise forms.ValidationError("Kapasite en az 1 olmalıdır.")
        return value

    def clean_max_duration_hours(self):
        value = self.cleaned_data["max_duration_hours"]
        if not 1 <= value <= 12:
            raise forms.ValidationError("Süre 1 ile 12 saat arasında olmalıdır.")
        return value

    def clean_weekly_limit(self):
        value = self.cleaned_data["weekly_limit"]
        if value < 1:
            raise forms.ValidationError("Haftalık hak en az 1 olmalıdır.")
        return value

    def clean_max_advance_days(self):
        value = self.cleaned_data["max_advance_days"]
        if not 1 <= value <= 60:
            raise forms.ValidationError("1 ile 60 gün arasında bir değer girin.")
        return value

    def clean(self):
        # TR: Aynı binada aynı isimde ikinci bir alan olmasın. Karşılaştırma Python'da yapılır, çünkü
        #     SQLite Türkçe harflerde (Ç/ç, Ş/ş, İ/i) büyük-küçük harf farkını doğru karşılaştırmaz.
        # ES: Que no haya dos espacios con el mismo nombre en el mismo edificio. Se compara en Python porque
        #     SQLite no compara bien mayúsculas/minúsculas con letras turcas (Ç/ç, Ş/ş, İ/i).
        cleaned = super().clean()
        name, building = cleaned.get("name"), cleaned.get("building")
        if name and building:
            key = (normalize(name), normalize(building))
            others = Space.objects.exclude(pk=self.instance.pk) if self.instance.pk else Space.objects.all()
            if any((normalize(s.name), normalize(s.building)) == key for s in others.only("name", "building")):
                raise forms.ValidationError("Bu binada aynı isimde bir alan zaten var.")
        return cleaned


def normalize(text):
    """
    TR: Karşılaştırma için metni Türkçe kurallarıyla küçük harfe çevirir (I→ı, İ→i) ve boşlukları sadeleştirir.
    ES: Pasa el texto a minúsculas con las reglas del turco (I→ı, İ→i) y simplifica los espacios para compararlo.
    """
    text = " ".join(text.split()).replace("I", "ı").replace("İ", "i")
    return text.lower()

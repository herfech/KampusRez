"""
TR: Geliştirme ve sunum için örnek alanlar oluşturur. Çalıştırmak için: python manage.py demo_data
ES: Crea espacios de ejemplo para desarrollo y presentación. Para ejecutarlo: python manage.py demo_data
"""
from django.core.management.base import BaseCommand

from spaces.models import Space

DEMO_SPACES = [
    # TR: Derslikler: onay gerekir, en fazla 3 saat / ES: Aulas: requieren aprobación, máximo 3 horas
    {"name": "D-101", "space_type": Space.SpaceType.CLASSROOM, "building": "Mühendislik Fakültesi", "floor": "1",
     "capacity": 40, "equipment": "Projeksiyon, akıllı tahta", "requires_approval": True, "max_duration_hours": 3},
    {"name": "D-204", "space_type": Space.SpaceType.CLASSROOM, "building": "Mühendislik Fakültesi", "floor": "2",
     "capacity": 60, "equipment": "Projeksiyon, ses sistemi", "requires_approval": True, "max_duration_hours": 3},
    # TR: Laboratuvarlar: onay gerekir / ES: Laboratorios: requieren aprobación
    {"name": "Bilgisayar Lab 1", "space_type": Space.SpaceType.LAB, "building": "Mühendislik Fakültesi", "floor": "Zemin",
     "capacity": 30, "equipment": "30 bilgisayar, projeksiyon", "requires_approval": True, "weekly_limit": 2},
    {"name": "Bilgisayar Lab 2", "space_type": Space.SpaceType.LAB, "building": "Meslek Yüksekokulu", "floor": "1",
     "capacity": 24, "equipment": "24 bilgisayar", "requires_approval": True, "weekly_limit": 2},
    # TR: Çalışma alanları: anında onay / ES: Salas de estudio: aprobación inmediata
    {"name": "Çalışma Odası A", "space_type": Space.SpaceType.STUDY_ROOM, "building": "Merkez Kütüphane", "floor": "2",
     "capacity": 6, "equipment": "Beyaz tahta, ekran"},
    {"name": "Çalışma Odası B", "space_type": Space.SpaceType.STUDY_ROOM, "building": "Merkez Kütüphane", "floor": "2",
     "capacity": 8, "equipment": "Beyaz tahta"},
]


class Command(BaseCommand):
    help = "Örnek alanlar oluşturur (aynı isimde alan varsa atlar)."

    def handle(self, *args, **options):
        created = 0
        for data in DEMO_SPACES:
            # TR: Aynı alan iki kez oluşturulmasın / ES: Evitar crear el mismo espacio dos veces
            _, was_created = Space.objects.get_or_create(
                name=data["name"], building=data["building"], defaults=data
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(f"{created} yeni alan oluşturuldu."))

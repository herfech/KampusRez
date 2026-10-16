#!/usr/bin/env python
"""
TR: Django'nun komut satırı yönetim aracı (runserver, migrate vb.).
ES: Herramienta de línea de comandos de Django (runserver, migrate, etc.).
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django bulunamadı. Sanal ortamı (venv) etkinleştirdiniz mi? "
            "'pip install -r requirements.txt' komutunu çalıştırın."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

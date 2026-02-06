"""
Crea un superusuario desde variables de entorno si no existe.
Uso en Render (sin Shell): añadir al Start Command y definir:
  DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea superusuario desde env vars si no existe. Para Render sin Shell.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '').strip()

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                'ensure_superuser: faltan DJANGO_SUPERUSER_* en env. Omitiendo.'
            ))
            return

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS(
                'ensure_superuser: ya existe un superusuario.'
            ))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(
            f'ensure_superuser: superusuario "{username}" creado.'
        ))

"""
Comando: asigna username a usuarios que lo tengan vacío o igual a '',
usando la parte del correo antes de @ (o el email completo si hace falta).
Uso: python manage.py fix_username_from_email
     python manage.py fix_username_from_email --email donatodistefano4@gmail.com
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


def username_from_email(email):
    """Genera un username único a partir del email (parte antes de @)."""
    if not email:
        return None
    base = email.split('@')[0].lower().replace('.', '').replace('+', '')[:30]
    if not base:
        return email[:30]  # fallback
    return base


class Command(BaseCommand):
    help = 'Asigna username a usuarios que lo tengan vacío, usando su email.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Correo del usuario a corregir (opcional). Si no se pasa, se revisan todos.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se haría, sin guardar.',
        )

    def handle(self, *args, **options):
        email_filter = options.get('email')
        dry_run = options.get('dry_run', False)

        if email_filter:
            users = list(User.objects.filter(email__iexact=email_filter))
        else:
            # Usuarios con username vacío o solo espacios
            users = [u for u in User.objects.all() if not (u.username or '').strip()]

        if not users and email_filter:
            self.stdout.write(self.style.WARNING(f'No hay usuario con email "{email_filter}".'))
            return
        if not users:
            self.stdout.write(self.style.SUCCESS('No hay usuarios con username vacío.'))
            return

        for user in users:
            new_username = username_from_email(user.email or '')
            if not new_username:
                self.stdout.write(self.style.WARNING(f'Usuario pk={user.pk} sin email, saltando.'))
                continue
            # Asegurar unicidad
            candidate = new_username
            n = 0
            while User.objects.filter(username=candidate).exclude(pk=user.pk).exists():
                n += 1
                candidate = f"{new_username}{n}"[:30]
            new_username = candidate

            self.stdout.write(f'  {user.email} -> username="{new_username}"')
            if not dry_run:
                user.username = new_username
                user.save(update_fields=['username'])
                self.stdout.write(self.style.SUCCESS(f'  Actualizado pk={user.pk}.'))

        if dry_run:
            self.stdout.write(self.style.WARNING('(dry-run: no se guardó nada)'))
        else:
            self.stdout.write(self.style.SUCCESS('Listo.'))

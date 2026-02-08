# backend/accounts/management/commands/make_user_staff.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = (
        'Convierte un usuario en Administrador (is_staff) o Gestor BD (is_superuser). '
        'Por defecto crea Administrador (panel de solicitudes). Usa --superuser para Gestor BD (panel en /panel-interno-mux/).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'email_or_username',
            type=str,
            help='Email o nombre de usuario del usuario a promover.',
        )
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Conceder is_superuser (Gestor BD: acceso al panel Django en /panel-interno-mux/).',
        )

    def handle(self, *args, **options):
        email_or_username = options['email_or_username'].strip()
        make_superuser = options['superuser']

        user = User.objects.filter(email=email_or_username).first()
        if not user:
            user = User.objects.filter(username=email_or_username).first()
        if not user:
            self.stderr.write(
                self.style.ERROR(f'No se encontró usuario con email o username: {email_or_username}')
            )
            return

        user.is_staff = True
        if make_superuser:
            user.is_superuser = True
        user.save()
        self.stdout.write(
            self.style.SUCCESS(
                f'Usuario "{user.email}" (username: {user.username}) es ahora administrador.'
                + (' (superuser)' if make_superuser else '')
            )
        )

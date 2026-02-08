"""
Reset total de usuarios y creación de Admin + Gestor BD.

Elimina TODOS los usuarios (y en cascada: pedidos, carritos, mensajes, etc.)
y crea dos usuarios nuevos:
  1. Administrador (is_staff): panel de solicitudes
  2. Gestor BD (is_superuser): panel Django en /panel-interno-mux/

Uso:
  python manage.py reset_and_setup_users
  python manage.py reset_and_setup_users --no-input  # usa variables de entorno
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


def _username_from_email(email):
    """Genera username único a partir del email."""
    base = email.split('@')[0].replace('.', '_')[:30]
    i = 0
    while True:
        uname = base if i == 0 else f'{base}{i}'
        if not User.objects.filter(username=uname).exists():
            return uname
        i += 1


class Command(BaseCommand):
    help = (
        'Elimina todos los usuarios y crea Administrador + Gestor BD. '
        'Los pedidos, carritos y datos relacionados se borran en cascada.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='No pedir datos; usar env vars ADMIN_EMAIL, ADMIN_PASSWORD, GESTOR_EMAIL, GESTOR_PASSWORD',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='No pedir confirmación antes de borrar.',
        )

    def handle(self, *args, **options):
        no_input = options['no_input']
        force = options['force']

        if no_input:
            admin_email = os.environ.get('ADMIN_EMAIL', '').strip()
            admin_password = os.environ.get('ADMIN_PASSWORD', '').strip()
            gestor_email = os.environ.get('GESTOR_EMAIL', '').strip()
            gestor_password = os.environ.get('GESTOR_PASSWORD', '').strip()
            if not all([admin_email, admin_password, gestor_email, gestor_password]):
                self.stderr.write(self.style.ERROR(
                    'Con --no-input se requieren: ADMIN_EMAIL, ADMIN_PASSWORD, GESTOR_EMAIL, GESTOR_PASSWORD'
                ))
                return
        else:
            self.stdout.write(self.style.WARNING(
                'Este comando eliminará TODOS los usuarios y sus datos (pedidos, carritos, etc.).'
            ))
            if not force:
                confirm = input('¿Continuar? [y/N]: ')
                if confirm.lower() != 'y':
                    self.stdout.write('Cancelado.')
                    return

            admin_email = input('Email del Administrador (panel solicitudes): ').strip()
            admin_password = input('Contraseña del Administrador: ')
            gestor_email = input('Email del Gestor BD (panel Django): ').strip()
            gestor_password = input('Contraseña del Gestor BD: ')

            if not admin_email or not admin_password or not gestor_email or not gestor_password:
                self.stderr.write(self.style.ERROR('Todos los campos son obligatorios.'))
                return

        # Eliminar todos los usuarios
        count = User.objects.count()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Eliminados {count} usuario(s).'))

        # Crear Administrador (is_staff, NO superuser)
        admin = User.objects.create_user(
            username=_username_from_email(admin_email),
            email=admin_email,
            password=admin_password,
            is_staff=True,
            is_superuser=False,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Administrador creado: {admin_email} (panel de solicitudes)'
        ))

        # Crear Gestor BD (is_staff + is_superuser)
        gestor = User.objects.create_user(
            username=_username_from_email(gestor_email),
            email=gestor_email,
            password=gestor_password,
            is_staff=True,
            is_superuser=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Gestor BD creado: {gestor_email} (panel en /panel-interno-mux/)'
        ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Listo. Inicia sesión con cualquiera de los dos correos.'))

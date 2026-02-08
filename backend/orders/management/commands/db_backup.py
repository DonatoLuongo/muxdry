# orders/management/commands/db_backup.py
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
import os
import subprocess
import gzip
from datetime import datetime


class Command(BaseCommand):
    help = 'Hace respaldo de la base de datos (PostgreSQL o SQLite)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir', type=str, default='/var/backups/muxdry',
            help='Carpeta donde guardar el respaldo'
        )
        parser.add_argument(
            '--keep', type=int, default=4,
            help='Número de semanas de respaldos a conservar'
        )

    def handle(self, *args, **options):
        backup_dir = options['dir']
        keep_weeks = options['keep']
        os.makedirs(backup_dir, exist_ok=True)

        db_engine = settings.DATABASES['default']['ENGINE']

        if 'postgresql' in db_engine:
            self._backup_postgresql(backup_dir, keep_weeks)
        elif 'sqlite' in db_engine:
            self._backup_sqlite(backup_dir, keep_weeks)
        else:
            self.stderr.write(f'Motor de BD no soportado: {db_engine}')
            return

    def _backup_postgresql(self, backup_dir, keep_weeks):
        db = settings.DATABASES['default']
        ts = datetime.now().strftime('%Y-%m-%d_%H%M')
        out_file = os.path.join(backup_dir, f'muxdry_{ts}.sql')

        env = os.environ.copy()
        if db.get('PASSWORD'):
            env['PGPASSWORD'] = db['PASSWORD']

        cmd = [
            'pg_dump',
            '-h', db.get('HOST', 'localhost'),
            '-p', str(db.get('PORT', 5432)),
            '-U', db.get('USER', 'postgres'),
            '-d', db['NAME'],
            '--no-owner', '--no-acl', '-F', 'p',
            '-f', out_file,
        ]
        subprocess.run(cmd, env=env, check=True)
        self.stdout.write(f'Respaldo SQL: {out_file}')

        with open(out_file, 'rb') as f_in:
            with gzip.open(f'{out_file}.gz', 'wb') as f_out:
                f_out.writelines(f_in)
        os.remove(out_file)
        self.stdout.write(self.style.SUCCESS(f'Respaldo comprimido: {out_file}.gz'))

        # Limpiar antiguos
        import glob
        import time
        pattern = os.path.join(backup_dir, 'muxdry_*.sql.gz')
        cutoff = time.time() - (keep_weeks * 7 * 24 * 3600)
        for path in glob.glob(pattern):
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
                self.stdout.write(f'Eliminado antiguo: {path}')

    def _backup_sqlite(self, backup_dir, keep_weeks):
        db = settings.DATABASES['default']
        db_path = db['NAME']
        if not os.path.exists(db_path):
            self.stderr.write(f'No existe {db_path}')
            return

        ts = datetime.now().strftime('%Y-%m-%d_%H%M')
        out_file = os.path.join(backup_dir, f'muxdry_sqlite_{ts}.sqlite3')
        import shutil
        shutil.copy2(db_path, out_file)

        with open(out_file, 'rb') as f_in:
            with gzip.open(f'{out_file}.gz', 'wb') as f_out:
                f_out.writelines(f_in)
        os.remove(out_file)
        self.stdout.write(self.style.SUCCESS(f'Respaldo: {out_file}.gz'))

        import glob
        import time
        pattern = os.path.join(backup_dir, 'muxdry_sqlite_*.sqlite3.gz')
        cutoff = time.time() - (keep_weeks * 7 * 24 * 3600)
        for path in glob.glob(pattern):
            if os.path.getmtime(path) < cutoff:
                os.remove(path)

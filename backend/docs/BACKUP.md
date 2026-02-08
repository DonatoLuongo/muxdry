# Respaldos de base de datos (Backup)

## Opción 1: Comando Django (recomendado)

Usa la configuración de Django (`.env`, `settings.py`) para conectar a la BD. Soporta PostgreSQL y SQLite.

```bash
cd backend
python manage.py db_backup --dir /var/backups/muxdry --keep 4
```

### Cron semanal

```bash
crontab -e

# Respaldar cada domingo a las 2:00 AM
0 2 * * 0 cd /ruta/a/muxdry-1/backend && python manage.py db_backup --dir /var/backups/muxdry >> /var/log/muxdry-backup.log 2>&1
```

---

## Opción 2: Scripts shell

Para PostgreSQL (cuando `pg_dump` está instalado):

```bash
./backend/scripts/backup_db.sh /var/backups/muxdry
```

Para SQLite:

```bash
./backend/scripts/backup_sqlite.sh /var/backups/muxdry
```

---

## Restaurar un respaldo PostgreSQL

```bash
# Archivo comprimido
gunzip -c /var/backups/muxdry/muxdry_2026-02-09_0200.sql.gz | psql -U postgres -d muxdry_restore -f -

# O con el script
./backend/scripts/restore_db.sh /var/backups/muxdry/muxdry_2026-02-09_0200.sql.gz muxdry_restore
```

---

## Dónde guardar los respaldos

1. **Mismo servidor**: `/var/backups/muxdry/` (permisos: `chmod 700`)
2. **Disco externo / NFS**: montar y usar esa ruta
3. **Nube**: tras el respaldo, copiar con `aws s3 cp`, `rclone` o similar

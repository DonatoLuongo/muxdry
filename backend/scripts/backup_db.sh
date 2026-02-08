#!/bin/bash
# Respaldo semanal de base de datos PostgreSQL - MUXDRY
# Uso: ./backup_db.sh [ruta_carpeta_backups]
# Cron ejemplo (domingos 2:00): 0 2 * * 0 /ruta/backend/scripts/backup_db.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${1:-/var/backups/muxdry}"
KEEP_WEEKS=4

# Crear carpeta de respaldos si no existe
mkdir -p "$BACKUP_DIR"

# Cargar variables de .env si existe
if [ -f "$BACKEND_DIR/.env" ]; then
    set -a
    source "$BACKEND_DIR/.env" 2>/dev/null || true
    set +a
fi

# Obtener credenciales de DATABASE_URL o DB_*
if [ -n "$DATABASE_URL" ]; then
    # Parsear DATABASE_URL (postgres://user:pass@host:port/dbname)
    DB_NAME=$(echo "$DATABASE_URL" | sed -n 's/.*\/\([^?]*\).*/\1/p')
    DB_USER=$(echo "$DATABASE_URL" | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_PASS=$(echo "$DATABASE_URL" | sed -n 's/.*\/\/[^:]*:\([^@]*\)@.*/\1/p')
else
    DB_NAME="${DB_NAME:-muxdry}"
    DB_USER="${DB_USER:-postgres}"
    DB_HOST="${DB_HOST:-localhost}"
    DB_PORT="${DB_PORT:-5432}"
fi

TIMESTAMP=$(date +%Y-%m-%d_%H%M)
BACKUP_FILE="$BACKUP_DIR/muxdry_${TIMESTAMP}.sql"

# Exportar PGPASSWORD si está definida (evita prompt)
export PGPASSWORD="${DB_PASSWORD:-$DB_PASS}"

echo "[$(date)] Iniciando respaldo a $BACKUP_FILE"

# Ejecutar pg_dump
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --no-owner --no-acl -F p -f "$BACKUP_FILE"

# Comprimir para ahorrar espacio
gzip -f "$BACKUP_FILE"
BACKUP_FILE="${BACKUP_FILE}.gz"

echo "[$(date)] Respaldo completado: $BACKUP_FILE"

# Eliminar respaldos antiguos (mantener últimos KEEP_WEEKS)
find "$BACKUP_DIR" -name "muxdry_*.sql.gz" -mtime +$((KEEP_WEEKS * 7)) -delete 2>/dev/null || true

echo "[$(date)] Limpieza de respaldos antiguos (>${KEEP_WEEKS} semanas) realizada"
unset PGPASSWORD

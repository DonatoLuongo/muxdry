#!/bin/bash
# Restaurar respaldo PostgreSQL - MUXDRY
# Uso: ./restore_db.sh archivo.sql [nombre_bd_destino]
# Ejemplo: ./restore_db.sh /var/backups/muxdry/muxdry_2026-02-09_0200.sql.gz muxdry_restore

set -e

BACKUP_FILE="$1"
DB_DEST="${2:-muxdry}"

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    echo "Uso: $0 archivo.sql [nombre_bd_destino]"
    echo "Ejemplo: $0 /var/backups/muxdry/muxdry_2026-02-09_0200.sql.gz muxdry"
    exit 1
fi

# Si está comprimido, descomprimir a temporal
if [[ "$BACKUP_FILE" == *.gz ]]; then
    TEMP_SQL=$(mktemp)
    gunzip -c "$BACKUP_FILE" > "$TEMP_SQL"
    SQL_FILE="$TEMP_SQL"
else
    SQL_FILE="$BACKUP_FILE"
fi

# Cargar .env si existe
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
if [ -f "$BACKEND_DIR/.env" ]; then
    set -a
    source "$BACKEND_DIR/.env" 2>/dev/null || true
    set +a
fi

DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
export PGPASSWORD="${DB_PASSWORD:-}"

echo "Creando base de datos $DB_DEST si no existe..."
createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_DEST" 2>/dev/null || true

echo "Restaurando desde $BACKUP_FILE..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_DEST" -f "$SQL_FILE"

[ -n "$TEMP_SQL" ] && rm -f "$TEMP_SQL"
unset PGPASSWORD
echo "Restauración completada en base de datos: $DB_DEST"

#!/bin/bash
# Respaldo semanal de SQLite - MUXDRY (desarrollo o despliegue simple)
# Uso: ./backup_sqlite.sh [ruta_carpeta_backups]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
DB_FILE="${DB_FILE:-$BACKEND_DIR/db.sqlite3}"
BACKUP_DIR="${1:-/var/backups/muxdry}"
KEEP_WEEKS=4

mkdir -p "$BACKUP_DIR"

if [ ! -f "$DB_FILE" ]; then
    echo "[$(date)] ERROR: No existe $DB_FILE"
    exit 1
fi

TIMESTAMP=$(date +%Y-%m-%d_%H%M)
BACKUP_FILE="$BACKUP_DIR/muxdry_sqlite_${TIMESTAMP}.sqlite3"

echo "[$(date)] Copiando $DB_FILE a $BACKUP_FILE"
cp "$DB_FILE" "$BACKUP_FILE"
gzip -f "$BACKUP_FILE"

echo "[$(date)] Respaldo completado: ${BACKUP_FILE}.gz"

# Eliminar respaldos antiguos
find "$BACKUP_DIR" -name "muxdry_sqlite_*.sqlite3.gz" -mtime +$((KEEP_WEEKS * 7)) -delete 2>/dev/null || true

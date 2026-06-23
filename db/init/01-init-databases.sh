#!/bin/bash
# Provisions a database + role per service on first container start.
# Runs automatically via /docker-entrypoint-initdb.d.
set -euo pipefail

create_db() {
  local db="$1" user="$2" pass="$3"
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE ROLE ${user} WITH LOGIN PASSWORD '${pass}';
    CREATE DATABASE ${db} OWNER ${user};
    GRANT ALL PRIVILEGES ON DATABASE ${db} TO ${user};
EOSQL
}

create_db grafana "grafana" "${GRAFANA_DB_PASSWORD:-grafana}"
create_db wikijs  "wikijs"  "${WIKIJS_DB_PASSWORD:-wikijs}"
create_db zammad  "zammad"  "${ZAMMAD_DB_PASSWORD:-zammad}"

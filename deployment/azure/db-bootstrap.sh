#!/bin/sh
set -eu

# A temporary no-ingress Container App runs this once. Express environments
# support secret-backed environment references, but not secret volumes.
export PGHOST="${PGHOST:?PostgreSQL hostname required}"
export PGPORT=5432
export PGSSLMODE=verify-full
export PGSSLROOTCERT=/etc/ssl/cert.pem
export PGUSER=aletheia_admin
: "${DB_ADMIN_PASSWORD:?administrator secret required}"
: "${DB_OWNER_PASSWORD:?owner secret required}"
: "${DB_APP_PASSWORD:?application secret required}"
: "${DB_MLFLOW_PASSWORD:?MLflow secret required}"
export PGPASSWORD="$DB_ADMIN_PASSWORD"

psql --no-psqlrc --quiet --set=ON_ERROR_STOP=1 --dbname=postgres \
  --set="owner_password=$DB_OWNER_PASSWORD" \
  --set="app_password=$DB_APP_PASSWORD" \
  --set="mlflow_password=$DB_MLFLOW_PASSWORD" <<'SQL'
SELECT format('CREATE ROLE aletheia_owner LOGIN CREATEROLE PASSWORD %L', :'owner_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aletheia_owner') \gexec
SELECT format('CREATE ROLE aletheia_app LOGIN PASSWORD %L', :'app_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aletheia_app') \gexec
SELECT 'CREATE ROLE aletheia_runtime NOLOGIN'
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aletheia_runtime') \gexec
SELECT format('CREATE ROLE aletheia_mlflow LOGIN PASSWORD %L', :'mlflow_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aletheia_mlflow') \gexec
GRANT aletheia_runtime TO aletheia_owner WITH ADMIN OPTION;
GRANT aletheia_runtime TO aletheia_app;
SELECT 'CREATE DATABASE aletheia_app OWNER aletheia_owner'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'aletheia_app') \gexec
SELECT 'CREATE DATABASE aletheia_mlflow OWNER aletheia_mlflow'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'aletheia_mlflow') \gexec
REVOKE ALL ON DATABASE aletheia_app FROM PUBLIC;
REVOKE ALL ON DATABASE aletheia_mlflow FROM PUBLIC;
GRANT CONNECT ON DATABASE aletheia_app TO aletheia_app;
SQL

# Azure's managed databases may retain a public schema owner distinct from the
# new database owners. Grant CREATE only to each owner inside its own database.
psql --no-psqlrc --quiet --set=ON_ERROR_STOP=1 --dbname=aletheia_app \
  --command='GRANT USAGE, CREATE ON SCHEMA public TO aletheia_owner'
psql --no-psqlrc --quiet --set=ON_ERROR_STOP=1 --dbname=aletheia_mlflow \
  --command='GRANT USAGE, CREATE ON SCHEMA public TO aletheia_mlflow'

unset PGPASSWORD DB_ADMIN_PASSWORD DB_OWNER_PASSWORD DB_APP_PASSWORD
export PGUSER=aletheia_mlflow
export PGPASSWORD="$DB_MLFLOW_PASSWORD"
unset DB_MLFLOW_PASSWORD
# A failed restore can leave an incomplete schema. This archive contains no
# database/schema drop entry; --clean removes only its own partially restored
# objects. Once metadata is complete, later starts leave it untouched.
if ! psql --no-psqlrc --tuples-only --no-align --set=ON_ERROR_STOP=1 \
  --dbname=aletheia_mlflow \
  --command="SELECT CASE WHEN (SELECT COUNT(*) FROM model_versions)=1 AND (SELECT COUNT(*) FROM runs)=1 THEN 'mlflow_metadata_verified' ELSE 'mlflow_metadata_unexpected' END" \
  | grep -qx 'mlflow_metadata_verified'; then
  pg_restore --clean --if-exists --no-owner --no-acl --exit-on-error \
    --dbname=aletheia_mlflow /opt/aletheia/mlflow-seed.dump
fi

psql --no-psqlrc --tuples-only --no-align --set=ON_ERROR_STOP=1 \
  --dbname=aletheia_mlflow \
  --command="SELECT CASE WHEN (SELECT COUNT(*) FROM model_versions)=1 AND (SELECT COUNT(*) FROM runs)=1 THEN 'mlflow_metadata_verified' ELSE 'mlflow_metadata_unexpected' END" \
  | grep -qx 'mlflow_metadata_verified'
echo 'database roles, databases, verified TLS and approved MLflow metadata ready'

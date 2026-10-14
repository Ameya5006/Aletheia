#!/bin/sh
set -eu
# Values come only from generated/mounted secret files, never Git or image layers.
psql --username "$POSTGRES_USER" --dbname postgres --set ON_ERROR_STOP=1 \
  --set owner_password="$(cat /run/secrets/owner_password)" \
  --set app_password="$(cat /run/secrets/app_password)" \
  --set mlflow_password="$(cat /run/secrets/mlflow_password)" <<'SQL'
CREATE ROLE aletheia_owner LOGIN CREATEROLE PASSWORD :'owner_password';
CREATE ROLE aletheia_app LOGIN PASSWORD :'app_password';
CREATE ROLE aletheia_runtime NOLOGIN;
GRANT aletheia_runtime TO aletheia_owner WITH ADMIN OPTION;
GRANT aletheia_runtime TO aletheia_app;
CREATE ROLE aletheia_mlflow LOGIN PASSWORD :'mlflow_password';
CREATE DATABASE aletheia_app OWNER aletheia_owner;
CREATE DATABASE aletheia_mlflow OWNER aletheia_mlflow;
REVOKE ALL ON DATABASE aletheia_app FROM PUBLIC;
REVOKE ALL ON DATABASE aletheia_mlflow FROM PUBLIC;
GRANT CONNECT ON DATABASE aletheia_app TO aletheia_app;
SQL

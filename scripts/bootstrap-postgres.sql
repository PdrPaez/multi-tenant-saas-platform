-- Run once as a PostgreSQL superuser against saas_demo.
CREATE ROLE saas_owner LOGIN PASSWORD 'saas_owner_password' NOSUPERUSER NOBYPASSRLS;
CREATE ROLE saas_app LOGIN PASSWORD 'saas_app_password' NOSUPERUSER NOBYPASSRLS;
GRANT CONNECT ON DATABASE saas_demo TO saas_owner, saas_app;

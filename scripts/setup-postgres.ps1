param([string]$Database='saas_demo', [string]$HostName='localhost', [int]$Port=5432)
$env:DATABASE_ADMIN_URL="postgresql+psycopg://saas_owner:saas_owner_password@$HostName`:$Port/$Database"
$env:DATABASE_URL="postgresql+psycopg://saas_app:saas_app_password@$HostName`:$Port/$Database"
Write-Host 'Run scripts/bootstrap-postgres.sql as a PostgreSQL superuser first.'
Write-Host "DATABASE_ADMIN_URL=$env:DATABASE_ADMIN_URL"
Write-Host "DATABASE_URL=$env:DATABASE_URL"

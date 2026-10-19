param(
    [string]$ResourceGroup = 'rg-aletheia-showcase-sea-01',
    [string]$AppName = 'db-bootstrap',
    [string]$BackendDigest = 'sha256:4cddaada14267b60279364368d512a834e919ca19fe75523158872c5bbf37338',
    [ValidateSet('migrate', 'verify')]
    [string]$Operation = 'migrate'
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
if ($BackendDigest -notmatch '^sha256:[0-9a-f]{64}$') { throw 'Invalid backend digest' }

$subscription = (& az account show --query id -o tsv).Trim()
if ($LASTEXITCODE -ne 0 -or -not $subscription) { throw 'Azure subscription unavailable' }
$bearer = (& az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv).Trim()
if ($LASTEXITCODE -ne 0 -or -not $bearer) { throw 'Azure ARM token unavailable' }
$headers = @{ Authorization = "Bearer $bearer" }
$sub = Invoke-RestMethod -Uri "https://management.azure.com/subscriptions/${subscription}?api-version=2022-12-01" -Headers $headers
if ($sub.state -ne 'Enabled' -or $sub.subscriptionPolicies.spendingLimit -ne 'On' -or $sub.subscriptionPolicies.quotaId -notlike 'AzureForStudents*') {
    throw 'Student spending protection unavailable'
}
$appId = (& az containerapp show -g $ResourceGroup -n $AppName --query id -o tsv).Trim()
$state = (& az containerapp show -g $ResourceGroup -n $AppName --query properties.runningStatus -o tsv).Trim()
if ($LASTEXITCODE -ne 0 -or $state -ne 'Stopped') { throw 'Temporary bootstrap app must be stopped before migration' }
$secretResponse = & az rest --method post --url "https://management.azure.com${appId}/listSecrets?api-version=2024-03-01" -o json
if ($LASTEXITCODE -ne 0) { throw 'Azure secret lookup failed' }
$secrets = @{}
foreach ($item in ($secretResponse | ConvertFrom-Json).value) { $secrets[$item.name] = $item.value }
foreach ($name in @('admin-password', 'owner-password', 'app-password', 'mlflow-password')) {
    if ($secrets[$name] -notmatch '^[0-9a-f]{64}$') { throw "Missing or malformed Azure secret: $name" }
}
$hostName = 'pg-aletheia-sea-1017.postgres.database.azure.com'
$ownerDbUrl = "postgresql+psycopg://aletheia_owner:$($secrets['owner-password'])@${hostName}:5432/aletheia_app?sslmode=verify-full&sslrootcert=/etc/ssl/certs/ca-certificates.crt"
$templateJson = & az bicep build --file (Join-Path $PSScriptRoot 'db-migrate-app.bicep') --stdout
if ($LASTEXITCODE -ne 0) { throw 'Migration template failed to build' }
$values = @{
    backendImage = "acraletheiasea1017.azurecr.io/backend@$BackendDigest"
    operation = $Operation
    administratorPassword = $secrets['admin-password']
    ownerPassword = $secrets['owner-password']
    appPassword = $secrets['app-password']
    mlflowPassword = $secrets['mlflow-password']
    ownerDbUrl = $ownerDbUrl
}
$parameters = @{}
foreach ($key in $values.Keys) { $parameters[$key] = @{ value = $values[$key] } }
$body = @{ properties = @{ mode = 'Incremental'; template = ($templateJson | ConvertFrom-Json); parameters = $parameters } } | ConvertTo-Json -Depth 100 -Compress
$url = "https://management.azure.com/subscriptions/$subscription/resourceGroups/$ResourceGroup/providers/Microsoft.Resources/deployments/aletheia-db-$Operation-20261018?api-version=2022-09-01"
try { $null = Invoke-RestMethod -Method Put -Uri $url -Headers $headers -ContentType 'application/json' -Body $body }
catch { throw 'Migration app deployment PUT failed; credentials suppressed' }
for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Seconds 10
    $result = Invoke-RestMethod -Method Get -Uri $url -Headers $headers
    if ($result.properties.provisioningState -eq 'Succeeded') { break }
    if ($result.properties.provisioningState -in @('Failed', 'Canceled')) { throw "Migration app deployment failed: $($result.properties.error.code); credentials suppressed" }
}
if ($result.properties.provisioningState -ne 'Succeeded') { throw 'Migration app deployment timed out; credentials suppressed' }
$null = & az rest --method post --url "https://management.azure.com${appId}/start?api-version=2025-07-01" -o none
if ($LASTEXITCODE -ne 0) { throw 'Migration app start failed; credentials suppressed' }
Write-Output "Temporary $Operation app started with owner-only, certificate-verified database URL in Azure secret handling."

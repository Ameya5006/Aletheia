param(
    [string]$ResourceGroup = 'rg-aletheia-showcase-sea-01',
    [string]$BootstrapApp = 'db-bootstrap',
    [string]$BackendDigest = 'sha256:dcaa62439a3330f436fa0715f8559dd7310b13e3edec1a987210c7bbb3b60a86',
    [string]$DeploymentPinPath = '/state/deployment.json'
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
if ($BackendDigest -notmatch '^sha256:[0-9a-f]{64}$') { throw 'Invalid backend digest' }
$subscription = (& az account show --query id -o tsv).Trim()
$bearer = (& az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv).Trim()
if ($LASTEXITCODE -ne 0 -or -not $subscription -or -not $bearer) { throw 'Azure context unavailable' }
$headers = @{ Authorization = "Bearer $bearer" }
$sub = Invoke-RestMethod -Uri "https://management.azure.com/subscriptions/${subscription}?api-version=2022-12-01" -Headers $headers
if ($sub.state -ne 'Enabled' -or $sub.subscriptionPolicies.spendingLimit -ne 'On' -or $sub.subscriptionPolicies.quotaId -notlike 'AzureForStudents*') {
    throw 'Student spending protection unavailable'
}
$bootstrapId = (& az containerapp show -g $ResourceGroup -n $BootstrapApp --query id -o tsv).Trim()
$secretResponse = & az rest --method post --url "https://management.azure.com${bootstrapId}/listSecrets?api-version=2024-03-01" -o json
if ($LASTEXITCODE -ne 0) { throw 'Bootstrap secret lookup failed' }
$password = (($secretResponse | ConvertFrom-Json).value | Where-Object name -eq 'app-password').value
if ($password -notmatch '^[0-9a-f]{64}$') { throw 'Application Azure secret unavailable' }
$front = (& az containerapp show -g $ResourceGroup -n frontend --query properties.configuration.ingress.fqdn -o tsv).Trim()
if ($LASTEXITCODE -ne 0 -or $front -notmatch '^frontend\.[a-z0-9-]+\.southeastasia\.azurecontainerapps\.io$') { throw 'Expected frontend HTTPS hostname unavailable' }
$hostName = 'pg-aletheia-sea-1017.postgres.database.azure.com'
$appDbUrl = "postgresql+psycopg://aletheia_app:${password}@${hostName}:5432/aletheia_app?sslmode=verify-full&sslrootcert=/etc/ssl/certs/ca-certificates.crt"
$templateJson = & az bicep build --file (Join-Path $PSScriptRoot 'backend-app.bicep') --stdout
if ($LASTEXITCODE -ne 0) { throw 'Backend template failed to build' }
$values = @{
    backendImage = "acraletheiasea1017.azurecr.io/backend@$BackendDigest"
    appDbUrl = $appDbUrl
    frontendHostName = $front
    deploymentPinPath = $DeploymentPinPath
}
$parameters = @{}
foreach ($key in $values.Keys) { $parameters[$key] = @{ value = $values[$key] } }
$body = @{ properties = @{ mode = 'Incremental'; template = ($templateJson | ConvertFrom-Json); parameters = $parameters } } | ConvertTo-Json -Depth 100 -Compress
$url = "https://management.azure.com/subscriptions/$subscription/resourceGroups/$ResourceGroup/providers/Microsoft.Resources/deployments/aletheia-backend-20261018?api-version=2022-09-01"
try { $null = Invoke-RestMethod -Method Put -Uri $url -Headers $headers -ContentType 'application/json' -Body $body }
catch { throw 'Backend app deployment PUT failed; credentials suppressed' }
for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Seconds 10
    $result = Invoke-RestMethod -Method Get -Uri $url -Headers $headers
    if ($result.properties.provisioningState -eq 'Succeeded') {
        Write-Output 'Backend app provisioned at 1 vCPU/2 GiB with internal HTTPS ingress and least-privilege Azure database secret.'
        exit 0
    }
    if ($result.properties.provisioningState -in @('Failed', 'Canceled')) { throw "Backend app deployment failed: $($result.properties.error.code); credentials suppressed" }
}
throw 'Backend app deployment timed out; credentials suppressed'

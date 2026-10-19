param(
    [string]$ResourceGroup = 'rg-aletheia-showcase-sea-01',
    [string]$ServerName = 'pg-aletheia-sea-1017',
    [string]$BootstrapImageDigest = 'sha256:5fb5ac7dcc3c9c44479d33829464be96a34e8e48f5287a09a0e5451efc9e08bd'
)
$ErrorActionPreference = 'Stop'

function New-RandomPassword {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    return ([BitConverter]::ToString($bytes) -replace '-', '').ToLowerInvariant()
}

$subscription = (& az account show --query id -o tsv).Trim()
$bearer = (& az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv).Trim()
if ($LASTEXITCODE -ne 0 -or -not $subscription -or -not $bearer) { throw 'Azure context unavailable' }
$headers = @{ Authorization = "Bearer $bearer" }
$sub = Invoke-RestMethod -Uri "https://management.azure.com/subscriptions/${subscription}?api-version=2022-12-01" -Headers $headers
if ($sub.state -ne 'Enabled' -or $sub.subscriptionPolicies.spendingLimit -ne 'On' -or $sub.subscriptionPolicies.quotaId -notlike 'AzureForStudents*') {
    throw 'Student spending protection unavailable'
}
$server = & az postgres flexible-server show -g $ResourceGroup -n $ServerName --query '{state:state,sku:sku.name,version:version}' -o json | ConvertFrom-Json
if ($server.state -ne 'Ready' -or $server.sku -ne 'Standard_B1ms' -or $server.version -ne '18') { throw 'Approved PostgreSQL server is not ready' }
$admin = New-RandomPassword
$owner = New-RandomPassword
$app = New-RandomPassword
$mlflow = New-RandomPassword
$serverUrl = "https://management.azure.com/subscriptions/$subscription/resourceGroups/$ResourceGroup/providers/Microsoft.DBforPostgreSQL/flexibleServers/${ServerName}?api-version=2025-08-01"
try {
    $body = @{ properties = @{ administratorLoginPassword = $admin } } | ConvertTo-Json -Compress
    $null = Invoke-RestMethod -Method Patch -Uri $serverUrl -Headers $headers -ContentType 'application/json' -Body $body
} catch { throw 'PostgreSQL password reset failed; secret suppressed' }
for ($i = 0; $i -lt 90; $i++) {
    Start-Sleep -Seconds 10
    $state = & az postgres flexible-server show -g $ResourceGroup -n $ServerName --query state -o tsv
    if ($state -eq 'Ready') { break }
}
if ($state -ne 'Ready') { throw 'PostgreSQL password reset did not return to Ready' }
Write-Output 'PostgreSQL administrator password rotated in memory.'

$templateJson = & az bicep build --file (Join-Path $PSScriptRoot 'db-bootstrap-app.bicep') --stdout
if ($LASTEXITCODE -ne 0) { throw 'Bootstrap app template failed to build' }
$template = $templateJson | ConvertFrom-Json
$values = @{
    serverName = $ServerName
    bootstrapImage = "acraletheiasea1017.azurecr.io/db-bootstrap@$BootstrapImageDigest"
    administratorPassword = $admin
    ownerPassword = $owner
    appPassword = $app
    mlflowPassword = $mlflow
}
$parameters = @{}
foreach ($key in $values.Keys) { $parameters[$key] = @{ value = $values[$key] } }
$body = @{ properties = @{ mode = 'Incremental'; template = $template; parameters = $parameters } } | ConvertTo-Json -Depth 100 -Compress
$url = "https://management.azure.com/subscriptions/$subscription/resourceGroups/$ResourceGroup/providers/Microsoft.Resources/deployments/aletheia-db-bootstrap-app-20261017?api-version=2022-09-01"
try { $null = Invoke-RestMethod -Method Put -Uri $url -Headers $headers -ContentType 'application/json' -Body $body }
catch { throw 'Bootstrap app deployment PUT failed; credentials suppressed' }
for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Seconds 10
    $result = Invoke-RestMethod -Method Get -Uri $url -Headers $headers
    if ($result.properties.provisioningState -eq 'Succeeded') {
        Write-Output 'Bootstrap app provisioned with Azure secret values; no secret printed.'
        exit 0
    }
    if ($result.properties.provisioningState -in @('Failed', 'Canceled')) {
        throw "Bootstrap app deployment failed: $($result.properties.error.code); credentials suppressed"
    }
}
throw 'Bootstrap app deployment timed out; credentials suppressed'

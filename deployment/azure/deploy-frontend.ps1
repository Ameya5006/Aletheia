param(
    [string]$ResourceGroup = 'rg-aletheia-showcase-sea-01',
    [string]$FrontendDigest = 'sha256:b8920e2338c285ba564e8a96c33b1dea208c6a580c2e1f49de1b87ad1d1fe073',
    [string]$PublicJwks = '{"keys":[]}'
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
if ($FrontendDigest -notmatch '^sha256:[0-9a-f]{64}$') { throw 'Invalid frontend digest' }
try {
    $keys = ($PublicJwks | ConvertFrom-Json).keys
    if ($null -eq $keys -or @($keys).Count -gt 32) { throw 'Invalid JWKS key list' }
} catch { throw 'Invalid public JWKS' }
$subscription = (& az account show --query id -o tsv).Trim()
$bearer = (& az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv).Trim()
if ($LASTEXITCODE -ne 0 -or -not $subscription -or -not $bearer) { throw 'Azure context unavailable' }
$headers = @{ Authorization = "Bearer $bearer" }
$sub = Invoke-RestMethod -Uri "https://management.azure.com/subscriptions/${subscription}?api-version=2022-12-01" -Headers $headers
if ($sub.state -ne 'Enabled' -or $sub.subscriptionPolicies.spendingLimit -ne 'On' -or $sub.subscriptionPolicies.quotaId -notlike 'AzureForStudents*') {
    throw 'Student spending protection unavailable'
}
$templateJson = & az bicep build --file (Join-Path $PSScriptRoot 'frontend-app.bicep') --stdout
if ($LASTEXITCODE -ne 0) { throw 'Frontend template failed to build' }
$values = @{
    environmentName = 'cae-aletheia-sea-01'
    registryName = 'acraletheiasea1017'
    pullIdentityName = 'id-aletheia-pull-sea-01'
    frontendImage = "acraletheiasea1017.azurecr.io/frontend@$FrontendDigest"
    publicIngress = $true
    publicJwks = $PublicJwks
}
$parameters = @{}
foreach ($key in $values.Keys) { $parameters[$key] = @{ value = $values[$key] } }
$body = @{ properties = @{ mode = 'Incremental'; template = ($templateJson | ConvertFrom-Json); parameters = $parameters } } | ConvertTo-Json -Depth 100 -Compress
$url = "https://management.azure.com/subscriptions/$subscription/resourceGroups/$ResourceGroup/providers/Microsoft.Resources/deployments/aletheia-frontend-20261018?api-version=2022-09-01"
try { $null = Invoke-RestMethod -Method Put -Uri $url -Headers $headers -ContentType 'application/json' -Body $body }
catch { throw 'Frontend app deployment PUT failed' }
for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Seconds 10
    $result = Invoke-RestMethod -Method Get -Uri $url -Headers $headers
    if ($result.properties.provisioningState -eq 'Succeeded') {
        Write-Output 'Existing public frontend updated with certificate-verified HTTPS backend proxy.'
        exit 0
    }
    if ($result.properties.provisioningState -in @('Failed', 'Canceled')) { throw "Frontend app deployment failed: $($result.properties.error.code)" }
}
throw 'Frontend app deployment timed out'

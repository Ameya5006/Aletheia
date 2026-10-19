# Preserved failed PATCH attempt. Azure did not apply its requested change.
# Use configure-operator-smoke-secret-bicep.ps1 for the validated update.
throw 'Historical failed PATCH attempt is disabled; evidence retained.'
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$privateKeyPath = 'artifacts/azure-preflight/cloud-private/signing.pem'
if (-not (Test-Path -LiteralPath $privateKeyPath)) { throw 'Ignored local signing material unavailable' }
$key = Get-Content -LiteralPath $privateKeyPath -Raw
if ($key -notmatch 'BEGIN PRIVATE KEY' -or $key -notmatch 'END PRIVATE KEY') { throw 'Signing material malformed' }
$sid = (az account show --query id -o tsv --only-show-errors).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Azure account unavailable' }
$resource = "/subscriptions/$sid/resourceGroups/rg-aletheia-workload-sea-01/providers/Microsoft.App/containerApps/release-operator"
$url = "https://management.azure.com${resource}?api-version=2025-07-01"
$secretUrl = "https://management.azure.com${resource}/listSecrets?api-version=2025-07-01"
$token = (az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv --only-show-errors).Trim()
if ($LASTEXITCODE -ne 0) { throw 'ARM access token unavailable' }
$headers = @{ Authorization = "Bearer $token" }
$phase = 'get'
try {
    $app = Invoke-RestMethod -Method Get -Uri $url -Headers $headers
    if ($app.properties.runningStatus -ne 'Stopped' -or $app.properties.configuration.ingress) { throw 'Operator must be stopped without ingress' }
    $phase = 'listSecrets'
    $listed = Invoke-RestMethod -Method Post -Uri $secretUrl -Headers $headers -ContentType 'application/json' -Body '{}'
    $existing = @($listed.value | Where-Object { $_.name -in @('owner-db-url','operator-token') })
    if ($existing.Count -ne 2 -or @($existing | Where-Object { -not $_.value }).Count) { throw 'Existing Azure secrets unavailable' }
    $secrets = @($existing | ForEach-Object { @{ name = $_.name; value = $_.value } }) + @(@{ name = 'smoke-signing-key'; value = $key })
    $containers = @($app.properties.template.containers)
    if ($containers.Count -ne 1) { throw 'Unexpected operator container count' }
    $env = @($containers[0].env | Where-Object name -ne 'AZURE_SMOKE_SIGNING_KEY') + @(@{ name = 'AZURE_SMOKE_SIGNING_KEY'; secretRef = 'smoke-signing-key' })
    $container = @{
        name = $containers[0].name
        image = $containers[0].image
        command = @($containers[0].command)
        args = @($containers[0].args)
        resources = $containers[0].resources
        env = $env
    }
    $body = @{ properties = @{ configuration = @{ secrets = $secrets }; template = @{ containers = @($container); scale = $app.properties.template.scale } } } | ConvertTo-Json -Depth 100 -Compress
    $phase = 'patch'
    $null = Invoke-RestMethod -Method Patch -Uri $url -Headers $headers -ContentType 'application/json' -Body $body
} catch {
    $status = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 'none' }
    throw "Azure-managed smoke signing secret $phase failed (HTTP $status, $($_.Exception.GetType().Name)); response suppressed"
} finally {
    $key = $null; $secrets = $null; $body = $null; $token = $null
}
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Seconds 5
    $app = az containerapp show -g rg-aletheia-workload-sea-01 -n release-operator -o json --only-show-errors | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) { throw 'Operator readback unavailable' }
    if ($app.properties.provisioningState -eq 'Succeeded') { break }
}
if ($app.properties.runningStatus -ne 'Stopped' -or $app.properties.configuration.ingress) { throw 'Operator boundary changed unexpectedly' }
if (-not @($app.properties.configuration.secrets | Where-Object name -eq 'smoke-signing-key').Count) { throw 'Smoke secret reference missing' }
if (-not @($app.properties.template.containers[0].env | Where-Object { $_.name -eq 'AZURE_SMOKE_SIGNING_KEY' -and $_.secretRef -eq 'smoke-signing-key' }).Count) { throw 'Smoke secret environment reference missing' }
Write-Output 'Stopped no-ingress operator holds Azure-managed smoke signing reference; value suppressed.'

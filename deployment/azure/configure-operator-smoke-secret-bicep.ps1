$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$privateKeyPath = 'artifacts/azure-preflight/cloud-private/signing.pem'
if (-not (Test-Path -LiteralPath $privateKeyPath)) { throw 'Ignored local signing material unavailable' }
$key = [string]::Copy((Get-Content -LiteralPath $privateKeyPath -Raw))
if ($key -notmatch 'BEGIN PRIVATE KEY' -or $key -notmatch 'END PRIVATE KEY') { throw 'Signing material malformed' }
$sid = (az account show --query id -o tsv --only-show-errors).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Azure account unavailable' }
$resource = "/subscriptions/$sid/resourceGroups/rg-aletheia-workload-sea-01/providers/Microsoft.App/containerApps/release-operator"
$url = "https://management.azure.com${resource}?api-version=2025-07-01"
$secretUrl = "https://management.azure.com${resource}/listSecrets?api-version=2025-07-01"
$token = (az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv --only-show-errors).Trim()
if ($LASTEXITCODE -ne 0) { throw 'ARM access token unavailable' }
$headers = @{ Authorization = "Bearer $token" }
$phase = 'read'
try {
    Write-Output 'Operator update phase: read'
    $app = Invoke-RestMethod -Method Get -Uri $url -Headers $headers -TimeoutSec 45
    if ($app.properties.runningStatus -ne 'Stopped' -or $app.properties.configuration.ingress) { throw 'Operator must be stopped without ingress' }
    $phase = 'listSecrets'
    Write-Output 'Operator update phase: listSecrets (values suppressed)'
    $listed = Invoke-RestMethod -Method Post -Uri $secretUrl -Headers $headers -ContentType 'application/json' -Body '{}' -TimeoutSec 45
    $owner = @($listed.value | Where-Object name -eq 'owner-db-url')[0].value
    $operatorToken = @($listed.value | Where-Object name -eq 'operator-token')[0].value
    if (-not $owner -or -not $operatorToken) { throw 'Existing Azure-managed operator secrets unavailable' }
    $image = $app.properties.template.containers[0].image
    if ($image -notmatch '^acraletheiasea1017\.azurecr\.io/backend@sha256:[0-9a-f]{64}$') { throw 'Unexpected operator image' }
    $phase = 'bicep-build'
    Write-Output 'Operator update phase: Bicep build'
    $templateText = az bicep build --file (Join-Path $PSScriptRoot 'operator-app.bicep') --stdout --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw 'Operator Bicep build failed' }
    Write-Output 'Operator update phase: assemble secure parameters'
    $params = @{
        environmentName = @{ value = 'cae-aletheia-workload-sea-01' }
        backendImage = @{ value = $image }
        ownerDbUrl = @{ value = $owner }
        operatorToken = @{ value = $operatorToken }
        smokeSigningKey = @{ value = $key }
    }
    Write-Output 'Operator update phase: serialize secure ARM request'
    $template = ($templateText -join "`n") | ConvertFrom-Json
    $body = @{ properties = @{ mode = 'Incremental'; template = $template; parameters = $params } } | ConvertTo-Json -Depth 20 -Compress
    Write-Output 'Operator update phase: serialized request ready'
    $root = "https://management.azure.com/subscriptions/$sid/resourceGroups/rg-aletheia-workload-sea-01/providers/Microsoft.Resources/deployments/aletheia-operator-smoke-secret-20261018"
    $phase = 'validate'
    Write-Output 'Operator update phase: ARM validation'
    $validation = Invoke-RestMethod -Method Post -Uri "${root}/validate?api-version=2022-09-01" -Headers $headers -ContentType 'application/json' -Body $body -TimeoutSec 90
    if ($validation.properties.provisioningState -ne 'Succeeded') { throw 'ARM validation not successful' }
    $phase = 'what-if'
    Write-Output 'Operator update phase: ARM what-if'
    $preview = Invoke-WebRequest -Method Post -Uri "${root}/whatIf?api-version=2022-09-01" -Headers $headers -ContentType 'application/json' -Body $body -UseBasicParsing -TimeoutSec 90
    if ($preview.StatusCode -eq 202) {
        $pollUrl = $preview.Headers['Location']
        if (-not $pollUrl) { $pollUrl = $preview.Headers['Azure-AsyncOperation'] }
        if (-not $pollUrl) { throw 'What-if poll URL unavailable' }
        for ($attempt = 0; $attempt -lt 60; $attempt++) {
            Start-Sleep -Seconds 3
            $preview = Invoke-WebRequest -Method Get -Uri $pollUrl -Headers $headers -UseBasicParsing -TimeoutSec 45
            if ($preview.StatusCode -eq 200 -and $preview.Content) { break }
        }
    }
    $changes = @((($preview.Content | ConvertFrom-Json).properties.changes))
    if (@($changes | Where-Object { $_.changeType -notin @('Modify','Ignore') }).Count -or
        @($changes | Where-Object { $_.changeType -eq 'Modify' -and $_.resourceId -notlike '*/providers/Microsoft.App/containerApps/release-operator' }).Count) {
        throw 'Unexpected resource change in operator what-if'
    }
    Write-Output 'Operator secret Bicep validation and bounded what-if passed.'
    $phase = 'deploy'
    Write-Output 'Operator update phase: ARM deploy'
    $null = Invoke-RestMethod -Method Put -Uri "${root}?api-version=2022-09-01" -Headers $headers -ContentType 'application/json' -Body $body -TimeoutSec 90
} catch {
    $status = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 'none' }
    throw "Azure-managed smoke signing secret $phase failed (HTTP $status, $($_.Exception.GetType().Name)); response suppressed"
} finally {
    $key = $null; $owner = $null; $operatorToken = $null; $body = $null; $token = $null
}
for ($attempt = 0; $attempt -lt 90; $attempt++) {
    Start-Sleep -Seconds 10
    $status = az deployment group show -g rg-aletheia-workload-sea-01 -n aletheia-operator-smoke-secret-20261018 --query properties.provisioningState -o tsv --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw 'Operator deployment status unavailable' }
    if ($status -eq 'Succeeded') { break }
    if ($status -in @('Failed','Canceled')) { throw "Operator deployment $status; details suppressed" }
}
$app = az containerapp show -g rg-aletheia-workload-sea-01 -n release-operator -o json --only-show-errors | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or $app.properties.runningStatus -ne 'Stopped' -or $app.properties.configuration.ingress) { throw 'Operator boundary changed unexpectedly' }
if (-not @($app.properties.configuration.secrets | Where-Object name -eq 'smoke-signing-key').Count) { throw 'Smoke secret reference missing' }
if (-not @($app.properties.template.containers[0].env | Where-Object { $_.name -eq 'AZURE_SMOKE_SIGNING_KEY' -and $_.secretRef -eq 'smoke-signing-key' }).Count) { throw 'Smoke environment reference missing' }
Write-Output 'Stopped no-ingress operator holds Azure-managed smoke signing reference; value suppressed.'

param(
    [string]$ResourceGroup = 'rg-aletheia-showcase-sea-01',
    [string]$BootstrapApp = 'db-bootstrap',
    [string]$MlflowDigest = 'sha256:9e0ac611e997d415a916c5e12b176d184bd40a41bb5fd6913daa3f95ee388947'
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
if ($MlflowDigest -notmatch '^sha256:[0-9a-f]{64}$') { throw 'Invalid MLflow digest' }
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
$password = (($secretResponse | ConvertFrom-Json).value | Where-Object name -eq 'mlflow-password').value
if ($password -notmatch '^[0-9a-f]{64}$') { throw 'MLflow Azure secret unavailable' }
$hostName = 'pg-aletheia-sea-1017.postgres.database.azure.com'
$mlflowDbUrl = "postgresql+psycopg://aletheia_mlflow:${password}@${hostName}:5432/aletheia_mlflow?sslmode=verify-full&sslrootcert=/etc/ssl/certs/ca-certificates.crt"
$templateJson = & az bicep build --file (Join-Path $PSScriptRoot 'mlflow-app.bicep') --stdout
if ($LASTEXITCODE -ne 0) { throw 'MLflow template failed to build' }
$values = @{
    mlflowImage = "acraletheiasea1017.azurecr.io/mlflow@$MlflowDigest"
    mlflowDbUrl = $mlflowDbUrl
}
$parameters = @{}
foreach ($key in $values.Keys) { $parameters[$key] = @{ value = $values[$key] } }
$body = @{ properties = @{ mode = 'Incremental'; template = ($templateJson | ConvertFrom-Json); parameters = $parameters } } | ConvertTo-Json -Depth 100 -Compress
$url = "https://management.azure.com/subscriptions/$subscription/resourceGroups/$ResourceGroup/providers/Microsoft.Resources/deployments/aletheia-mlflow-20261018?api-version=2022-09-01"
try { $null = Invoke-RestMethod -Method Put -Uri $url -Headers $headers -ContentType 'application/json' -Body $body }
catch { throw 'MLflow app deployment PUT failed; credentials suppressed' }
for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Seconds 10
    $result = Invoke-RestMethod -Method Get -Uri $url -Headers $headers
    if ($result.properties.provisioningState -eq 'Succeeded') {
        Write-Output 'MLflow app provisioned with internal HTTPS ingress and Azure secret reference.'
        exit 0
    }
    if ($result.properties.provisioningState -in @('Failed', 'Canceled')) { throw "MLflow app deployment failed: $($result.properties.error.code); credentials suppressed" }
}
throw 'MLflow app deployment timed out; credentials suppressed'

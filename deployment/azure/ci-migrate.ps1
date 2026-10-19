param(
    [Parameter(Mandatory)][ValidatePattern('^sha256:[0-9a-f]{64}$')][string]$BackendDigest,
    [ValidateSet('Migration','Smoke')][string]$Task = 'Migration'
)
$ErrorActionPreference = 'Stop'
$group = 'rg-aletheia-workload-sea-01'
$name = 'release-operator'
$app = az containerapp show -g $group -n $name -o json --only-show-errors | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or $app.properties.runningStatus -ne 'Stopped' -or $app.properties.configuration.ingress) { throw 'No-ingress migration app must be stopped' }
if (-not @($app.properties.configuration.secrets | Where-Object name -eq 'owner-db-url').Count) { throw 'Azure owner secret reference missing' }
if ($Task -eq 'Smoke' -and -not @($app.properties.configuration.secrets | Where-Object name -eq 'smoke-signing-key').Count) { throw 'Azure-managed smoke signing reference missing' }
$image = "acraletheiasea1017.azurecr.io/backend@$BackendDigest"
$manifest = az acr manifest show-metadata -r acraletheiasea1017 -n "backend@$BackendDigest" --query digest -o tsv --only-show-errors 2>$null
if ($LASTEXITCODE -ne 0 -or $manifest.Trim() -ne $BackendDigest) { throw 'Immutable migration image unavailable' }
$subscription = (az account show --query id -o tsv --only-show-errors).Trim()
$url = "https://management.azure.com/subscriptions/$subscription/resourceGroups/$group/providers/Microsoft.App/containerApps/$name/stop?api-version=2025-07-01"
$command = if ($Task -eq 'Migration') { '/usr/local/bin/aletheia-ci-migrate' } else { '/usr/local/bin/aletheia-ci-smoke' }
$marker = if ($Task -eq 'Migration') { 'aletheia-migration-complete 0004_case_input' } else { 'aletheia-smoke-complete' }
try {
    $null = az containerapp update -g $group -n $name --image $image --command $command --args '' --min-replicas 1 --max-replicas 1 -o none --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw "$Task revision update failed" }
    $null = az rest --method post --url ($url -replace '/stop\?', '/start?') -o none --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw "$Task revision start failed" }
    $complete = $false
    for ($attempt = 0; $attempt -lt 90; $attempt++) {
        Start-Sleep -Seconds 10
        $logs = az containerapp logs show -g $group -n $name --type console --tail 60 --format text --only-show-errors 2>$null
        if ($LASTEXITCODE -eq 0) {
            $logText = $logs -join "`n"
            if ($logText -match 'BEGIN (RSA )?PRIVATE KEY|postgresql(\+psycopg)?://|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}') {
                throw 'Credential-like operator console log content detected; values suppressed'
            }
            if ($logText.Contains($marker)) { $complete = $true; break }
        }
    }
    if (-not $complete) { throw "$Task completion marker missing; inspect protected Azure logs" }
    Write-Output "Controlled no-ingress $Task completed."
} finally {
    $null = az rest --method post --url $url -o none --only-show-errors
    if ($LASTEXITCODE -ne 0) { throw 'Release operator stop failed; inspect immediately' }
    Write-Output 'Controlled release operator stopped.'
}

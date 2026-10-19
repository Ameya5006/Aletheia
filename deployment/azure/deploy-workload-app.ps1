param(
    [ValidateSet('mlflow','api','frontend')][string]$Kind,
    [string]$SharedGroup = 'rg-aletheia-showcase-sea-01',
    [string]$ResourceGroup = 'rg-aletheia-workload-sea-01',
    [string]$EnvironmentName = 'cae-aletheia-workload-sea-01'
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Read-Az([string[]]$Arguments, [string]$Failure) {
    $raw = & az @Arguments --only-show-errors 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { throw $Failure }
    return ($raw -join "`n")
}

$account = Read-Az @('account','show','-o','json') 'Azure account unavailable' | ConvertFrom-Json
if ($account.name -ne 'Azure for Students' -or $account.state -ne 'Enabled') { throw 'Student subscription unavailable' }
$sid = $account.id
$policy = Read-Az @('rest','--method','get','--url',"https://management.azure.com/subscriptions/${sid}?api-version=2022-12-01",'-o','json') 'Spending policy unavailable' | ConvertFrom-Json
if ($policy.subscriptionPolicies.spendingLimit -ne 'On' -or $policy.subscriptionPolicies.quotaId -notlike 'AzureForStudents*') { throw 'Student spending protection unavailable' }
$environment = Read-Az @('containerapp','env','show','-g',$ResourceGroup,'-n',$EnvironmentName,'-o','json') 'Workload environment unavailable' | ConvertFrom-Json
if ($environment.properties.provisioningState -ne 'Succeeded' -or @($environment.properties.workloadProfiles).Count -ne 1 -or $environment.properties.workloadProfiles[0].workloadProfileType -ne 'Consumption') { throw 'Consumption-only workload environment not ready' }
$effectiveEnvironment = Read-Az @('rest','--method','get','--url',"https://management.azure.com/subscriptions/$sid/resourceGroups/$ResourceGroup/providers/Microsoft.App/managedEnvironments/${EnvironmentName}?api-version=2026-07-01",'-o','json') 'Current ARM environment read unavailable' | ConvertFrom-Json
if ($effectiveEnvironment.properties.environmentMode -ne 'WorkloadProfiles' -or $effectiveEnvironment.properties.provisioningState -ne 'Succeeded') { throw 'Effective ARM environment mode is not ready WorkloadProfiles' }
$domain = $environment.properties.defaultDomain
if ($domain -notmatch '^[a-z0-9-]+\.southeastasia\.azurecontainerapps\.io$') { throw 'Unexpected workload environment domain' }
$frontHost = "frontend.$domain"
$imageDigests = @{
    mlflow = 'sha256:062f3fb2700fa152d6cab44aeec154f44ade7c2116f63038dca1ccd38342ab5d'
    api = 'sha256:06f7bb2229fb1c77b6561afaeccdbf51c9a0243005fb0ea647a8d6de44f683ab'
    frontend = 'sha256:12176c6a16302f1f4208c7878ead164701c08704ad3620fddc744ada63547416'
}
$repo = if ($Kind -eq 'api') { 'backend' } else { $Kind }
$image = "acraletheiasea1017.azurecr.io/${repo}@$($imageDigests[$Kind])"
$manifest = Read-Az @('acr','manifest','show-metadata','-r','acraletheiasea1017','-n',"${repo}@$($imageDigests[$Kind])",'-o','json') 'Image manifest unavailable' | ConvertFrom-Json
if ($manifest.digest -ne $imageDigests[$Kind]) { throw 'Image digest mismatch' }

$parameters = @{
    environmentName = @{ value = $EnvironmentName }
    sharedResourceGroupName = @{ value = $SharedGroup }
    registryName = @{ value = 'acraletheiasea1017' }
    pullIdentityName = @{ value = 'id-aletheia-pull-sea-01' }
}
if ($Kind -in @('mlflow','api')) {
    $bootstrapId = (Read-Az @('containerapp','show','-g',$SharedGroup,'-n','db-bootstrap','--query','id','-o','tsv') 'Preserved bootstrap app unavailable').Trim()
    $secrets = Read-Az @('rest','--method','post','--url',"https://management.azure.com${bootstrapId}/listSecrets?api-version=2024-03-01",'-o','json') 'Azure-managed database secrets unavailable' | ConvertFrom-Json
    $secretName = if ($Kind -eq 'api') { 'app-password' } else { 'mlflow-password' }
    $password = @($secrets.value | Where-Object name -eq $secretName)[0].value
    if ($password -notmatch '^[0-9a-f]{64}$') { throw 'Required database secret missing or malformed' }
    $role = if ($Kind -eq 'api') { 'aletheia_app' } else { 'aletheia_mlflow' }
    $dbUrl = "postgresql+psycopg://${role}:${password}@pg-aletheia-sea-1017.postgres.database.azure.com:5432/$role" + '?sslmode=verify-full&sslrootcert=/etc/ssl/certs/ca-certificates.crt'
    if ($Kind -eq 'api') {
        $parameters.backendImage = @{ value = $image }
        $parameters.appDbUrl = @{ value = $dbUrl }
        $parameters.frontendHostName = @{ value = $frontHost }
        $parameters.deploymentPinPath = @{ value = '/state/deployment.json' }
    } else {
        $parameters.mlflowImage = @{ value = $image }
        $parameters.mlflowDbUrl = @{ value = $dbUrl }
    }
} else {
    $publicJwks = $env:ALETHEIA_PUBLIC_JWKS
    try { $keyCount = @(($publicJwks | ConvertFrom-Json).keys).Count } catch { throw 'Public JWKS unavailable' }
    if ($keyCount -lt 1 -or $keyCount -gt 4) { throw 'Public JWKS must contain 1-4 keys' }
    $parameters.frontendImage = @{ value = $image }
    $parameters.publicIngress = @{ value = $true }
    $parameters.publicJwks = @{ value = $publicJwks }
}

$templateName = if ($Kind -eq 'api') { 'backend-app.bicep' } else { "$Kind-app.bicep" }
$templatePath = Join-Path $PSScriptRoot $templateName
$templateJson = Read-Az @('bicep','build','--file',$templatePath,'--stdout') 'Bicep build failed' | ConvertFrom-Json
$body = @{ properties = @{ mode = 'Incremental'; template = $templateJson; parameters = $parameters } } | ConvertTo-Json -Depth 100 -Compress
$bearer = (Read-Az @('account','get-access-token','--resource','https://management.azure.com/','--query','accessToken','-o','tsv') 'Azure ARM token unavailable').Trim()
$headers = @{ Authorization = "Bearer $bearer" }
$deploymentName = "aletheia-workload-$Kind-20261018"
$url = "https://management.azure.com/subscriptions/$sid/resourceGroups/$ResourceGroup/providers/Microsoft.Resources/deployments/${deploymentName}?api-version=2022-09-01"
try { $null = Invoke-RestMethod -Method Put -Uri $url -Headers $headers -ContentType 'application/json' -Body $body }
catch { throw "$Kind deployment PUT failed; response suppressed to protect secrets" }
$password = $null
$dbUrl = $null
$body = $null
for ($attempt = 0; $attempt -lt 90; $attempt++) {
    Start-Sleep -Seconds 10
    try { $status = Invoke-RestMethod -Method Get -Uri $url -Headers $headers }
    catch { throw "$Kind deployment status failed; response suppressed" }
    if ($status.properties.provisioningState -eq 'Succeeded') { Write-Output "$Kind deployment Succeeded at immutable digest $($imageDigests[$Kind])"; exit 0 }
    if ($status.properties.provisioningState -in @('Failed','Canceled')) { throw "$Kind deployment $($status.properties.provisioningState); error code $($status.properties.error.code); credentials suppressed" }
}
throw "$Kind deployment timed out; credentials suppressed"

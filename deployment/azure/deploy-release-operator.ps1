$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Read-Az([string[]]$Arguments, [string]$Failure) {
    $raw = & az @Arguments --only-show-errors 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { throw $Failure }
    return ($raw -join "`n")
}

$sid = (Read-Az @('account','show','--query','id','-o','tsv') 'Azure account unavailable').Trim()
$policy = Read-Az @('rest','--method','get','--url',"https://management.azure.com/subscriptions/${sid}?api-version=2022-12-01",'-o','json') 'Spending policy unavailable' | ConvertFrom-Json
if ($policy.subscriptionPolicies.spendingLimit -ne 'On') { throw 'Student spending protection unavailable' }
$group = 'rg-aletheia-workload-sea-01'
$envName = 'cae-aletheia-workload-sea-01'
$environment = Read-Az @('rest','--method','get','--url',"https://management.azure.com/subscriptions/$sid/resourceGroups/$group/providers/Microsoft.App/managedEnvironments/${envName}?api-version=2026-07-01",'-o','json') 'Environment unavailable' | ConvertFrom-Json
if ($environment.properties.environmentMode -ne 'WorkloadProfiles' -or $environment.properties.provisioningState -ne 'Succeeded' -or @($environment.properties.workloadProfiles).Count -ne 1 -or $environment.properties.workloadProfiles[0].workloadProfileType -ne 'Consumption') { throw 'Approved Consumption topology unavailable' }
$existing = Read-Az @('resource','list','-g',$group,'--query',"[?name=='release-operator'].id",'-o','json') 'Resource inventory unavailable' | ConvertFrom-Json
if ($existing -and @($existing).Count -gt 0) { throw 'Temporary operator app already exists; inspect before changing' }
$bootstrapId = (Read-Az @('containerapp','show','-g','rg-aletheia-showcase-sea-01','-n','db-bootstrap','--query','id','-o','tsv') 'Preserved bootstrap unavailable').Trim()
$bootstrapStatus = (Read-Az @('containerapp','show','-g','rg-aletheia-showcase-sea-01','-n','db-bootstrap','--query','properties.runningStatus','-o','tsv') 'Preserved bootstrap status unavailable').Trim()
if ($bootstrapStatus -ne 'Stopped') { throw 'Preserved Express bootstrap unexpectedly running' }
$secrets = Read-Az @('rest','--method','post','--url',"https://management.azure.com${bootstrapId}/listSecrets?api-version=2024-03-01",'-o','json') 'Azure-managed owner secret unavailable' | ConvertFrom-Json
$password = @($secrets.value | Where-Object name -eq 'owner-password')[0].value
if ($password -notmatch '^[0-9a-f]{64}$') { throw 'Owner secret missing or malformed' }
$tokenPath = 'artifacts/azure-preflight/cloud-private/administrator.token'
if (-not (Test-Path $tokenPath)) { throw 'Short-lived ignored operator token missing' }
$token = (Get-Content $tokenPath -Raw).Trim()
if ($token.Split('.').Count -ne 3) { throw 'Operator token malformed' }
$signingPath = 'artifacts/azure-preflight/cloud-private/signing.pem'
if (-not (Test-Path -LiteralPath $signingPath)) { throw 'Ignored showcase signing key missing' }
$signingKey = [string]::Copy((Get-Content -LiteralPath $signingPath -Raw))
if ($signingKey -notmatch 'BEGIN PRIVATE KEY') { throw 'Showcase signing key malformed' }
$digest = 'sha256:1a4fb60bd890e5b05f40cfd0896f377d020f71b60b3452cc6d23b216c12c8ac4'
$manifest = Read-Az @('acr','manifest','show-metadata','-r','acraletheiasea1017','-n',"backend@$digest",'-o','json') 'Approved backend manifest unavailable' | ConvertFrom-Json
if ($manifest.digest -ne $digest) { throw 'Backend digest mismatch' }
$url = 'postgresql+psycopg://aletheia_owner:' + $password + '@pg-aletheia-sea-1017.postgres.database.azure.com:5432/aletheia_app?sslmode=verify-full&sslrootcert=/etc/ssl/certs/ca-certificates.crt'
$templateText = Read-Az @('bicep','build','--file',(Join-Path $PSScriptRoot 'operator-app.bicep'),'--stdout') 'Operator Bicep build failed'
$parameters = @{
    environmentName = @{ value = $envName }
    backendImage = @{ value = "acraletheiasea1017.azurecr.io/backend@$digest" }
    ownerDbUrl = @{ value = $url }
    operatorToken = @{ value = $token }
    smokeSigningKey = @{ value = $signingKey }
}
$body = @{ properties = @{ mode = 'Incremental'; template = ($templateText | ConvertFrom-Json); parameters = $parameters } } | ConvertTo-Json -Depth 100 -Compress
$bearer = (Read-Az @('account','get-access-token','--resource','https://management.azure.com/','--query','accessToken','-o','tsv') 'ARM token unavailable').Trim()
$headers = @{ Authorization = "Bearer $bearer" }
$root = "https://management.azure.com/subscriptions/$sid/resourceGroups/$group/providers/Microsoft.Resources/deployments/aletheia-release-operator-20261018"
try {
    $phase = 'validate'
    $validation = Invoke-RestMethod -Method Post -Uri "${root}/validate?api-version=2022-09-01" -Headers $headers -ContentType 'application/json' -Body $body
    if ($validation.properties.provisioningState -ne 'Succeeded') { throw 'ARM validation did not succeed' }
    $phase = 'what-if'
    $whatIfResponse = Invoke-WebRequest -Method Post -Uri "${root}/whatIf?api-version=2022-09-01" -Headers $headers -ContentType 'application/json' -Body $body -UseBasicParsing
    Write-Output "Temporary operator what-if HTTP $([int]$whatIfResponse.StatusCode); header names: $(@($whatIfResponse.Headers.Keys) -join ',')"
    if ($whatIfResponse.StatusCode -eq 202) {
        $pollUrl = $whatIfResponse.Headers['Location']
        if (-not $pollUrl) { $pollUrl = $whatIfResponse.Headers['Azure-AsyncOperation'] }
        if (-not $pollUrl) { throw 'What-if asynchronous poll URL missing' }
        for ($j = 0; $j -lt 30; $j++) {
            Start-Sleep -Seconds 3
            $poll = Invoke-WebRequest -Method Get -Uri $pollUrl -Headers $headers -UseBasicParsing
            if ($poll.StatusCode -eq 200 -and $poll.Content) { break }
        }
        if (-not $poll.Content) { throw 'What-if asynchronous result unavailable' }
        $whatIf = $poll.Content | ConvertFrom-Json
    } else {
        $whatIf = $whatIfResponse.Content | ConvertFrom-Json
    }
    Write-Output "Temporary operator what-if response fields: $(@($whatIf.PSObject.Properties.Name) -join ','); nested fields: $(@($whatIf.properties.PSObject.Properties.Name) -join ',')"
    $changes = @($whatIf.properties.changes)
    Write-Output "Temporary operator what-if change count: $($changes.Count); kinds: $((@($changes | ForEach-Object { "$($_.changeType):$((($_.resourceId -split '/providers/')[-1] -split '/')[0])" }) -join ','))"
    $creates = @($changes | Where-Object changeType -eq 'Create')
    $unexpected = @($changes | Where-Object changeType -notin @('Create','Ignore'))
    if ($creates.Count -ne 1 -or $creates[0].resourceId -notlike '*/providers/Microsoft.App/containerApps/release-operator' -or $unexpected.Count -ne 0) { throw 'Unexpected temporary operator what-if' }
    Write-Output 'Temporary no-ingress operator ARM validation passed; what-if: one Container App create and four existing-resource ignores.'
    $phase = 'deploy'
    $null = Invoke-RestMethod -Method Put -Uri "${root}?api-version=2022-09-01" -Headers $headers -ContentType 'application/json' -Body $body
} catch {
    $httpStatus = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 'none' }
    throw "Temporary operator $phase failed (HTTP $httpStatus, $($_.Exception.GetType().Name)); details suppressed to protect credentials"
}
$password = $null; $token = $null; $signingKey = $null; $url = $null; $body = $null
for ($i = 0; $i -lt 90; $i++) {
    Start-Sleep -Seconds 10
    $status = Invoke-RestMethod -Method Get -Uri "${root}?api-version=2022-09-01" -Headers $headers
    if ($status.properties.provisioningState -eq 'Succeeded') { Write-Output 'Temporary no-ingress operator app provisioned.'; exit 0 }
    if ($status.properties.provisioningState -in @('Failed','Canceled')) { throw "Operator deployment $($status.properties.provisioningState), code $($status.properties.error.code); credentials suppressed" }
}
throw 'Operator deployment timed out; credentials suppressed'

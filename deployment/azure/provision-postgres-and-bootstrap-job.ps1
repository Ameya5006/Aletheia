param(
    [string]$ResourceGroup = 'rg-aletheia-showcase-sea-01',
    [string]$ServerName = 'pg-aletheia-sea-1017',
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^sha256:[0-9a-f]{64}$')]
    [string]$BootstrapImageDigest
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function New-RandomPassword {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    return ([BitConverter]::ToString($bytes) -replace '-', '').ToLowerInvariant()
}

function Invoke-ArmDeployment {
    param(
        [string]$Name,
        [string]$TemplatePath,
        [hashtable]$ParameterValues,
        [string]$Subscription,
        [string]$Bearer,
        [string]$Group
    )
    $templateJson = & az bicep build --file $TemplatePath --stdout
    if ($LASTEXITCODE -ne 0) { throw "Bicep build failed for $Name" }
    $template = $templateJson | ConvertFrom-Json
    $armParameters = @{}
    foreach ($key in $ParameterValues.Keys) {
        $armParameters[$key] = @{ value = $ParameterValues[$key] }
    }
    $body = @{
        properties = @{
            mode = 'Incremental'
            template = $template
            parameters = $armParameters
        }
    } | ConvertTo-Json -Depth 100 -Compress
    $url = "https://management.azure.com/subscriptions/$Subscription/resourceGroups/$Group/providers/Microsoft.Resources/deployments/${Name}?api-version=2022-09-01"
    $headers = @{ Authorization = "Bearer $Bearer" }
    try {
        $null = Invoke-RestMethod -Method Put -Uri $url -Headers $headers -ContentType 'application/json' -Body $body
    } catch {
        throw "ARM deployment $Name PUT failed; credentials suppressed."
    }
    for ($attempt = 0; $attempt -lt 180; $attempt++) {
        Start-Sleep -Seconds 10
        try {
            $result = Invoke-RestMethod -Method Get -Uri $url -Headers $headers
        } catch {
            throw "ARM deployment $Name status read failed; credentials suppressed."
        }
        $state = $result.properties.provisioningState
        if ($state -eq 'Succeeded') {
            Write-Output "DEPLOYMENT $Name Succeeded"
            return
        }
        if ($state -in @('Failed', 'Canceled')) {
            $code = $result.properties.error.code
            if (-not $code) { $code = 'Unknown' }
            throw "ARM deployment $Name $state, code $code; credentials suppressed."
        }
    }
    throw "ARM deployment $Name timed out; inspect resource state without printing secrets."
}

$subscription = (& az account show --query id -o tsv).Trim()
if ($LASTEXITCODE -ne 0 -or -not $subscription) { throw 'Azure subscription unavailable' }
$bearer = (& az account get-access-token --resource https://management.azure.com/ --query accessToken -o tsv).Trim()
if ($LASTEXITCODE -ne 0 -or -not $bearer) { throw 'Azure ARM token unavailable' }
$headers = @{ Authorization = "Bearer $bearer" }
$subscriptionState = Invoke-RestMethod -Method Get -Headers $headers -Uri "https://management.azure.com/subscriptions/${subscription}?api-version=2022-12-01"
if ($subscriptionState.state -ne 'Enabled' -or $subscriptionState.subscriptionPolicies.spendingLimit -ne 'On' -or $subscriptionState.subscriptionPolicies.quotaId -notlike 'AzureForStudents*') {
    throw 'Student offer or spending protection is not active'
}

$existing = & az postgres flexible-server list -g $ResourceGroup --query "[?name=='$ServerName'].name" -o tsv
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL inventory unavailable' }
if ($existing) {
    throw 'PostgreSQL server already exists; refusing to rotate its password implicitly'
}

$administratorPassword = New-RandomPassword
$ownerPassword = New-RandomPassword
$appPassword = New-RandomPassword
$mlflowPassword = New-RandomPassword

$directory = Split-Path -Parent $MyInvocation.MyCommand.Path
Invoke-ArmDeployment -Name 'aletheia-postgres-20261017' -TemplatePath (Join-Path $directory 'postgres-flexible.bicep') -ParameterValues @{
    serverName = $ServerName
    administratorPassword = $administratorPassword
} -Subscription $subscription -Bearer $bearer -Group $ResourceGroup

$image = "acraletheiasea1017.azurecr.io/db-bootstrap@$BootstrapImageDigest"
Invoke-ArmDeployment -Name 'aletheia-db-bootstrap-job-20261017' -TemplatePath (Join-Path $directory 'db-bootstrap-job.bicep') -ParameterValues @{
    serverName = $ServerName
    bootstrapImage = $image
    administratorPassword = $administratorPassword
    ownerPassword = $ownerPassword
    appPassword = $appPassword
    mlflowPassword = $mlflowPassword
} -Subscription $subscription -Bearer $bearer -Group $ResourceGroup

Write-Output 'Student protection active; PostgreSQL and secret-backed manual bootstrap job provisioned.'

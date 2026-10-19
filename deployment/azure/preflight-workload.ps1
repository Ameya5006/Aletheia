param(
    [string]$ResourceGroup = 'rg-aletheia-showcase-sea-01',
    [string]$ReplacementGroup = 'rg-aletheia-workload-sea-01',
    [string]$Region = 'southeastasia'
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

function Read-AzJson([string]$Label, [string[]]$Arguments) {
    $raw = & az @Arguments --only-show-errors 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { throw "$Label failed; Azure error suppressed to protect identifiers" }
    return (($raw -join "`n") | ConvertFrom-Json)
}
function Require([bool]$Condition, [string]$Label) {
    if (-not $Condition) { throw "Preflight gate failed: $Label" }
    Write-Output "PASS $Label"
}

$account = Read-AzJson 'Selected subscription' @('account','show','-o','json')
Require ($account.name -eq 'Azure for Students' -and $account.state -eq 'Enabled') 'Azure for Students selected and enabled'
$sid = $account.id
$policy = Read-AzJson 'Subscription policy' @('rest','--method','get','--url',"https://management.azure.com/subscriptions/${sid}?api-version=2022-12-01",'-o','json')
Require ($policy.subscriptionPolicies.spendingLimit -eq 'On' -and $policy.subscriptionPolicies.quotaId -like 'AzureForStudents*') 'Student offer and spending limit On'
foreach ($provider in @('Microsoft.App','Microsoft.ContainerRegistry','Microsoft.DBforPostgreSQL','Microsoft.ManagedIdentity','Microsoft.Resources')) {
    $registration = Read-AzJson "Provider $provider" @('provider','show','-n',$provider,'-o','json')
    Require ($registration.registrationState -eq 'Registered') "$provider registered"
}
$profiles = Read-AzJson 'Regional workload profiles' @('containerapp','env','workload-profile','list-supported','-l',$Region,'-o','json')
Require (@($profiles | Where-Object name -eq 'Consumption').Count -eq 1) 'Southeast Asia supports Consumption workload profile'
$quota = Read-AzJson 'Regional Container Apps quota' @('rest','--method','get','--url',"https://management.azure.com/subscriptions/$sid/providers/Microsoft.App/locations/$Region/usages?api-version=2025-07-01",'-o','json')
$environmentQuota = @($quota.value | Where-Object { $_.name.value -eq 'ManagedEnvironmentCount' })[0]
Require ($null -ne $environmentQuota -and $environmentQuota.limit -gt $environmentQuota.currentValue) 'ManagedEnvironmentCount has one free slot'
Write-Output 'INFO Consumption-core quota is environment-scoped; query it immediately after environment creation before app deployment.'

$existing = Read-AzJson 'Existing resource inventory' @('resource','list','-g',$ResourceGroup,'-o','json')
Require ($existing.Count -eq 8) 'Eight existing resources preserved'
$apps = Read-AzJson 'Existing Container Apps' @('containerapp','list','-g',$ResourceGroup,'-o','json')
Require (@($apps | Where-Object { $_.properties.runningStatus -ne 'Stopped' }).Count -eq 0) 'All four Express apps stopped'
$server = Read-AzJson 'PostgreSQL server' @('postgres','flexible-server','show','-g',$ResourceGroup,'-n','pg-aletheia-sea-1017','-o','json')
Require ($server.state -eq 'Ready' -and $server.sku.name -eq 'Standard_B1ms' -and $server.storage.storageSizeGb -eq 32 -and $server.highAvailability.mode -eq 'Disabled') 'Existing PostgreSQL Ready at B1ms/32 GiB without HA'
$tls = Read-AzJson 'PostgreSQL TLS' @('postgres','flexible-server','parameter','show','-g',$ResourceGroup,'-s','pg-aletheia-sea-1017','-n','require_secure_transport','-o','json')
Require ($tls.value -eq 'ON') 'PostgreSQL requires TLS'
$firewall = @(Read-AzJson 'PostgreSQL firewall' @('postgres','flexible-server','firewall-rule','list','-g',$ResourceGroup,'-s','pg-aletheia-sea-1017','-o','json'))
Require ($firewall.Count -eq 1 -and $firewall[0].name -eq 'AllowAzureServicesShowcase' -and $firewall[0].startIpAddress -eq '0.0.0.0' -and $firewall[0].endIpAddress -eq '0.0.0.0') 'Only previously approved Azure-services showcase rule exists'

$registry = Read-AzJson 'ACR' @('acr','show','-g',$ResourceGroup,'-n','acraletheiasea1017','-o','json')
Require ($registry.sku.name -eq 'Standard' -and -not $registry.adminUserEnabled) 'Existing Standard ACR with admin user disabled'
$identity = Read-AzJson 'Pull identity' @('identity','show','-g',$ResourceGroup,'-n','id-aletheia-pull-sea-01','-o','json')
$roles = Read-AzJson 'ACR pull role' @('role','assignment','list','--assignee',$identity.principalId,'--scope',$registry.id,'-o','json')
Require (@($roles | Where-Object roleDefinitionName -eq 'AcrPull').Count -ge 1) 'Existing managed identity has ACR pull permission'
$digests = @{
    backend = 'sha256:1a4fb60bd890e5b05f40cfd0896f377d020f71b60b3452cc6d23b216c12c8ac4'
    mlflow = 'sha256:062f3fb2700fa152d6cab44aeec154f44ade7c2116f63038dca1ccd38342ab5d'
    frontend = 'sha256:d9fd13691ed4229fc4172cb5705dd60ac8e8422c2547838a48fcbc88609df312'
}
foreach ($name in @('backend','mlflow','frontend')) {
    $digest = $digests[$name]
    $manifest = Read-AzJson "$name manifest" @('acr','manifest','show-metadata','-r','acraletheiasea1017','-n',"${name}@$digest",'-o','json')
    Require ($manifest.digest -eq $digest) "$name immutable ACR digest exists"
}

$template = Join-Path $PSScriptRoot 'workload-deployment.bicep'
$compiled = & az bicep build --file $template --stdout 2>$null
if ($LASTEXITCODE -ne 0 -or -not $compiled) { throw 'Bicep compilation failed' }
$compiledText = $compiled -join "`n"
Require ($compiledText -notmatch 'Microsoft.Network/|Microsoft.OperationalInsights/workspaces|Microsoft.Storage/storageAccounts|Microsoft.App/jobs') 'No prohibited network, paid workspace, storage or job resources in deployment'
Require ($compiledText -match '"environmentMode"\s*:\s*"WorkloadProfiles"' -and $compiledText -match 'workloadProfileType' -and $compiledText -notmatch '"Dedicated"') 'Explicit WorkloadProfiles environment mode with only Consumption profile'
Require ((1.0 + 0.5 + 0.25) -le 4 -and (2.0 + 1.0 + 0.5) -le 8) 'Planned app allocations fit Consumption profile size'
Write-Output 'INFO Planned maximum simultaneous replicas: 1.75 vCPU/3.5 GiB; min 0/max 1 for each app.'

$imagePrefix = 'acraletheiasea1017.azurecr.io'
$parameters = @(
    "frontendImage=$imagePrefix/frontend@$($digests.frontend)",
    "backendImage=$imagePrefix/backend@$($digests.backend)",
    "mlflowImage=$imagePrefix/mlflow@$($digests.mlflow)",
    'appDbUrl=preflight-placeholder',
    'mlflowDbUrl=preflight-placeholder'
)
$validation = Read-AzJson 'ARM validation' (@('deployment','sub','validate','--name','aletheia-workload-preflight-20261018','--location',$Region,'--template-file',$template,'--parameters') + $parameters + @('-o','json'))
Require ($validation.properties.provisioningState -eq 'Succeeded') 'Subscription-scope Bicep validation succeeded'
$whatIf = Read-AzJson 'ARM what-if' (@('deployment','sub','what-if','--name','aletheia-workload-preflight-20261018','--location',$Region,'--template-file',$template,'--parameters') + $parameters + @('--result-format','ResourceIdOnly','--no-pretty-print','-o','json'))
$names = @($whatIf.changes | ForEach-Object { ($_.resourceId -split '/')[-1] } | Sort-Object)
$expected = @('api','cae-aletheia-workload-sea-01','frontend','mlflow',$ReplacementGroup) | Sort-Object
Require ($names.Count -eq 5 -and (($names -join ',') -eq ($expected -join ','))) 'What-if changes exactly the approved resource group, environment and three apps'
Require (@($whatIf.changes | Where-Object changeType -ne 'Create').Count -eq 0) 'What-if does not modify existing resources'
Write-Output 'INFO Migration 0004_case_input (head) is preserved in prior bootstrap evidence; live recheck requires a new authorized app context.'
Write-Output 'INFO Account-specific ACR and PostgreSQL free-benefit evidence and expiry are preserved in RESOURCE_GATE_SEA_20261017.md. Azure forecast remains unavailable.'
Write-Output 'PASS Comprehensive workload preflight completed without cloud provisioning.'

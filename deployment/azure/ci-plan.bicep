targetScope = 'resourceGroup'

// Read-only Bicep validation of the frozen existing topology. The CI deploy
// script updates only image fields on these named apps so Azure secret values
// remain in the existing Container Apps configuration.
resource environment 'Microsoft.App/managedEnvironments@2026-07-01' existing = {
  name: 'cae-aletheia-workload-sea-01'
}
resource frontend 'Microsoft.App/containerApps@2024-03-01' existing = {
  name: 'frontend'
}
resource api 'Microsoft.App/containerApps@2024-03-01' existing = {
  name: 'api'
}
resource mlflow 'Microsoft.App/containerApps@2024-03-01' existing = {
  name: 'mlflow'
}
resource operator 'Microsoft.App/containerApps@2024-03-01' existing = {
  name: 'release-operator'
}

output environmentMode string = environment.properties.environmentMode
output workloadProfiles array = environment.properties.workloadProfiles
output appIds array = [ frontend.id, api.id, mlflow.id, operator.id ]

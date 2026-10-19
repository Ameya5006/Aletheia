targetScope = 'subscription'

param resourceGroupName string = 'rg-aletheia-workload-sea-01'
param environmentName string = 'cae-aletheia-workload-sea-01'
param location string = 'southeastasia'

resource appResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: {
    project: 'aletheia'
    workload: 'student-showcase'
    costBoundary: 'free-allowances-only'
  }
}

module environment './phase1-environment.bicep' = {
  name: 'aletheia-workload-environment'
  scope: appResourceGroup
  params: {
    location: location
    environmentName: environmentName
  }
}

output environmentName string = environment.outputs.environmentName

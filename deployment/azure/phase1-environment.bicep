targetScope = 'resourceGroup'

@description('The selected single Azure region after quota and free-allowance checks.')
param location string = resourceGroup().location

@description('Name of the one Consumption Container Apps environment.')
param environmentName string

@description('Non-identifying project tags.')
param tags object = {
  project: 'aletheia'
  workload: 'student-showcase'
  costBoundary: 'free-allowances-only'
}

// No customer VNet, Dedicated workload profile or Log Analytics workspace.
resource environment 'Microsoft.App/managedEnvironments@2026-07-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    environmentMode: 'WorkloadProfiles'
    appLogsConfiguration: {
      destination: null
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

output environmentName string = environment.name
output defaultDomain string = environment.properties.defaultDomain

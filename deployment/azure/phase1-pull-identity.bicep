targetScope = 'resourceGroup'

param location string = resourceGroup().location
param identityName string

resource pullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: {
    project: 'aletheia'
    workload: 'student-showcase'
    purpose: 'acr-pull-only'
  }
}

output identityName string = pullIdentity.name

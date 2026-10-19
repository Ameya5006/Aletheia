targetScope = 'resourceGroup'

param location string = resourceGroup().location
param environmentName string
param registryName string
param pullIdentityName string
param sharedResourceGroupName string = 'rg-aletheia-showcase-sea-01'
param frontendName string = 'frontend'
@description('Full immutable ACR image reference ending in @sha256:<digest>.')
param frontendImage string
param publicIngress bool = false
@description('Public deployment JWKS only; defaults to an empty key list.')
param publicJwks string = '{"keys":[]}'

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' existing = {
  name: environmentName
}
resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: registryName
  scope: resourceGroup(sharedResourceGroupName)
}
resource pullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: pullIdentityName
  scope: resourceGroup(sharedResourceGroupName)
}

resource frontend 'Microsoft.App/containerApps@2024-03-01' = {
  name: frontendName
  location: location
  tags: {
    project: 'aletheia'
    workload: 'student-showcase'
    costBoundary: 'free-allowances-only'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${pullIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: environment.id
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Multiple'
      registries: [
        {
          server: registry.properties.loginServer
          identity: pullIdentity.id
        }
      ]
      ingress: {
        external: publicIngress
        targetPort: 8080
        transport: 'http'
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: frontendImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'OIDC_JWKS_PUBLIC'
              value: publicJwks
            }
            {
              name: 'BACKEND_HOST'
              value: 'api'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

output frontendName string = frontend.name

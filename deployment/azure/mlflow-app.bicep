targetScope = 'resourceGroup'

param location string = resourceGroup().location
param environmentName string = 'cae-aletheia-sea-01'
param registryName string = 'acraletheiasea1017'
param pullIdentityName string = 'id-aletheia-pull-sea-01'
param sharedResourceGroupName string = 'rg-aletheia-showcase-sea-01'
@description('Verified immutable MLflow runtime image reference.')
param mlflowImage string
@secure()
param mlflowDbUrl string

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

resource mlflow 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'mlflow'
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
        external: false
        targetPort: 5000
        transport: 'http'
        allowInsecure: false
        traffic: [ { latestRevision: true, weight: 100 } ]
      }
      secrets: [ { name: 'mlflow-db-url', value: mlflowDbUrl } ]
    }
    template: {
      containers: [
        {
          name: 'mlflow'
          image: mlflowImage
          args: [ 'mlflow' ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'AZURE_MLFLOW_DB_URL', secretRef: 'mlflow-db-url' }
            { name: 'PGSSLCERT', value: '/run/secrets/no-client-certificate' }
            { name: 'MLFLOW_SERVER_ENABLE_JOB_EXECUTION', value: 'false' }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          {
            name: 'http'
            http: { metadata: { concurrentRequests: '10' } }
          }
        ]
      }
    }
  }
}

output appName string = mlflow.name

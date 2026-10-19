targetScope = 'resourceGroup'

param location string = resourceGroup().location
param environmentName string = 'cae-aletheia-sea-01'
param registryName string = 'acraletheiasea1017'
param pullIdentityName string = 'id-aletheia-pull-sea-01'
@description('Verified immutable backend image reference.')
param backendImage string
@allowed([ 'migrate', 'verify' ])
param operation string = 'migrate'
@secure()
param administratorPassword string
@secure()
param ownerPassword string
@secure()
param appPassword string
@secure()
param mlflowPassword string
@secure()
param ownerDbUrl string

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' existing = {
  name: environmentName
}
resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: registryName
}
resource pullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: pullIdentityName
}

// Reuse the stopped, no-ingress bootstrap app. Express environments cannot
// create Jobs or mount Secret volumes, so migration receives an Azure secret
// through a secretRef environment value. The Python image is unchanged.
resource migrate 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'db-bootstrap'
  location: location
  tags: {
    project: 'aletheia'
    workload: 'student-showcase'
    purpose: 'temporary-one-time-database-migration'
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
      activeRevisionsMode: 'Single'
      registries: [
        {
          server: registry.properties.loginServer
          identity: pullIdentity.id
        }
      ]
      secrets: [
        { name: 'admin-password', value: administratorPassword }
        { name: 'owner-password', value: ownerPassword }
        { name: 'app-password', value: appPassword }
        { name: 'mlflow-password', value: mlflowPassword }
        { name: 'owner-db-url', value: ownerDbUrl }
      ]
    }
    template: {
      containers: [
        {
          name: 'db-bootstrap'
          image: backendImage
          command: [ 'python' ]
          args: operation == 'migrate' ? [ '-m', 'alembic', 'upgrade', 'head' ] : [ '-m', 'alembic', 'current' ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'ALETHEIA_MIGRATION_URL', secretRef: 'owner-db-url' }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}

output appName string = migrate.name

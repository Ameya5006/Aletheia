targetScope = 'resourceGroup'

param location string = resourceGroup().location
param environmentName string = 'cae-aletheia-sea-01'
param registryName string = 'acraletheiasea1017'
param pullIdentityName string = 'id-aletheia-pull-sea-01'
param serverName string = 'pg-aletheia-sea-1017'
@description('Immutable ACR digest reference, not a tag.')
param bootstrapImage string
@secure()
param administratorPassword string
@secure()
param ownerPassword string
@secure()
param appPassword string
@secure()
param mlflowPassword string

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' existing = {
  name: environmentName
}
resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: registryName
}
resource pullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: pullIdentityName
}

resource bootstrap 'Microsoft.App/jobs@2024-03-01' = {
  name: 'db-bootstrap'
  location: location
  tags: {
    project: 'aletheia'
    workload: 'student-showcase'
    purpose: 'one-time-database-bootstrap'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${pullIdentity.id}': {}
    }
  }
  properties: {
    environmentId: environment.id
    workloadProfileName: 'Consumption'
    configuration: {
      triggerType: 'Manual'
      manualTriggerConfig: {
        parallelism: 1
        replicaCompletionCount: 1
      }
      replicaRetryLimit: 0
      replicaTimeout: 1800
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
      ]
    }
    template: {
      containers: [
        {
          name: 'db-bootstrap'
          image: bootstrapImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'PGHOST'
              value: '${serverName}.postgres.database.azure.com'
            }
          ]
          volumeMounts: [
            {
              volumeName: 'secrets'
              mountPath: '/run/secrets'
            }
          ]
        }
      ]
      volumes: [
        {
          name: 'secrets'
          storageType: 'Secret'
        }
      ]
    }
  }
}

output jobName string = bootstrap.name

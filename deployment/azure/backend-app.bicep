targetScope = 'resourceGroup'

param location string = resourceGroup().location
param environmentName string = 'cae-aletheia-sea-01'
param registryName string = 'acraletheiasea1017'
param pullIdentityName string = 'id-aletheia-pull-sea-01'
param sharedResourceGroupName string = 'rg-aletheia-showcase-sea-01'
@description('Verified immutable backend runtime image reference.')
param backendImage string
@secure()
param appDbUrl string
@description('Existing Azure-managed frontend hostname, without scheme.')
param frontendHostName string
@description('Pin file path, updated to an immutable packaged path after release approval.')
param deploymentPinPath string = '/state/deployment.json'

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

var frontendOrigin = 'https://${frontendHostName}'
resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'api'
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
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
        traffic: [ { latestRevision: true, weight: 100 } ]
      }
      secrets: [ { name: 'app-db-url', value: appDbUrl } ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: backendImage
          args: [ 'api' ]
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
          env: [
            { name: 'AZURE_APP_DB_URL', secretRef: 'app-db-url' }
            { name: 'PGSSLCERT', value: '/run/secrets/no-client-certificate' }
            { name: 'APP_ENV', value: 'release' }
            { name: 'APP_RELEASE_ROOT', value: '/release/current' }
            { name: 'APP_RELEASE_SHA256', value: '65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271' }
            { name: 'APP_MODEL_VERSION', value: '1' }
            { name: 'OIDC_ISSUER', value: frontendOrigin }
            { name: 'OIDC_AUDIENCE', value: 'aletheia-api' }
            { name: 'OIDC_JWKS_URI', value: '${frontendOrigin}/.well-known/jwks.json' }
            { name: 'OIDC_MAX_TOKEN_LIFETIME_SECONDS', value: '900' }
            { name: 'PROVIDER_TOKEN_LIFETIME_SECONDS', value: '900' }
            { name: 'CORS_ORIGINS', value: '["${frontendOrigin}"]' }
            { name: 'DEPLOYMENT_PIN_PATH', value: deploymentPinPath }
            { name: 'MLFLOW_ENDPOINT', value: '{"scheme":"http","hostname":"mlflow","port":80}' }
            { name: 'SSL_CERT_FILE', value: '/usr/local/lib/python3.12/site-packages/certifi/cacert.pem' }
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

output appName string = api.name

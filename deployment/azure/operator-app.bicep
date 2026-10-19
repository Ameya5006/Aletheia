targetScope = 'resourceGroup'

param location string = resourceGroup().location
param environmentName string
param sharedResourceGroupName string = 'rg-aletheia-showcase-sea-01'
param backendImage string
@secure()
param ownerDbUrl string
@secure()
param operatorToken string
@secure()
param smokeSigningKey string

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' existing = {
  name: environmentName
}
resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: 'acraletheiasea1017'
  scope: resourceGroup(sharedResourceGroupName)
}
resource pullIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: 'id-aletheia-pull-sea-01'
  scope: resourceGroup(sharedResourceGroupName)
}

var origin = 'https://frontend.${environment.properties.defaultDomain}'
resource operator 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'release-operator'
  location: location
  tags: {
    project: 'aletheia'
    purpose: 'temporary-release-publication'
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
        { server: registry.properties.loginServer, identity: pullIdentity.id }
      ]
      secrets: [
        { name: 'owner-db-url', value: ownerDbUrl }
        { name: 'operator-token', value: operatorToken }
        { name: 'smoke-signing-key', value: smokeSigningKey }
      ]
    }
    template: {
      containers: [
        {
          name: 'release-operator'
          image: backendImage
          command: [ 'sh' ]
          args: [ '-c', 'sleep 1800' ]
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [
            { name: 'AZURE_OWNER_DB_URL', secretRef: 'owner-db-url' }
            { name: 'AZURE_OPERATOR_TOKEN', secretRef: 'operator-token' }
            { name: 'AZURE_SMOKE_SIGNING_KEY', secretRef: 'smoke-signing-key' }
            { name: 'APP_ENV', value: 'release' }
            { name: 'APP_RELEASE_ROOT', value: '/release/current' }
            { name: 'APP_RELEASE_SHA256', value: '65f2302cc9c4795142567296cc6b16143fad5abfe4df7b04152975748c2ec271' }
            { name: 'APP_MODEL_VERSION', value: '1' }
            { name: 'OIDC_ISSUER', value: origin }
            { name: 'OIDC_AUDIENCE', value: 'aletheia-api' }
            { name: 'OIDC_JWKS_URI', value: '${origin}/.well-known/jwks.json' }
            { name: 'OIDC_MAX_TOKEN_LIFETIME_SECONDS', value: '900' }
            { name: 'PROVIDER_TOKEN_LIFETIME_SECONDS', value: '900' }
            { name: 'BOOTSTRAP_OIDC_ISSUER', value: origin }
            { name: 'BOOTSTRAP_OIDC_SUB', value: 'synthetic-admin' }
            { name: 'DEPLOYMENT_PIN_PATH', value: '/state/deployment.json' }
            { name: 'MLFLOW_ENDPOINT', value: '{"scheme":"http","hostname":"mlflow","port":80}' }
            { name: 'PGSSLCERT', value: '/run/secrets/no-client-certificate' }
            { name: 'SSL_CERT_FILE', value: '/usr/local/lib/python3.12/site-packages/certifi/cacert.pem' }
          ]
        }
      ]
      scale: { minReplicas: 0, maxReplicas: 1 }
    }
  }
}

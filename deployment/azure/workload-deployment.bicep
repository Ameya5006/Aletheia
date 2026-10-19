targetScope = 'subscription'

@description('Approved Southeast Asia replacement resource group. Existing Express resources stay in the shared group.')
param resourceGroupName string = 'rg-aletheia-workload-sea-01'
param sharedResourceGroupName string = 'rg-aletheia-showcase-sea-01'
param location string = 'southeastasia'
param environmentName string = 'cae-aletheia-workload-sea-01'
param registryName string = 'acraletheiasea1017'
param pullIdentityName string = 'id-aletheia-pull-sea-01'
@description('Immutable image references ending in @sha256:<digest>.')
param frontendImage string
param backendImage string
param mlflowImage string
@secure()
param appDbUrl string
@secure()
param mlflowDbUrl string
@description('Public verification material only, never a signing key.')
param publicJwks string = '{"keys":[]}'

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

module mlflow './mlflow-app.bicep' = {
  name: 'aletheia-workload-mlflow'
  scope: appResourceGroup
  params: {
    location: location
    environmentName: environmentName
    sharedResourceGroupName: sharedResourceGroupName
    registryName: registryName
    pullIdentityName: pullIdentityName
    mlflowImage: mlflowImage
    mlflowDbUrl: mlflowDbUrl
  }
  dependsOn: [environment]
}

module api './backend-app.bicep' = {
  name: 'aletheia-workload-api'
  scope: appResourceGroup
  params: {
    location: location
    environmentName: environmentName
    sharedResourceGroupName: sharedResourceGroupName
    registryName: registryName
    pullIdentityName: pullIdentityName
    backendImage: backendImage
    appDbUrl: appDbUrl
    frontendHostName: 'frontend.${environment.outputs.defaultDomain}'
    deploymentPinPath: '/state/deployment.json'
  }
  dependsOn: [mlflow]
}

module frontend './frontend-app.bicep' = {
  name: 'aletheia-workload-frontend'
  scope: appResourceGroup
  params: {
    location: location
    environmentName: environmentName
    sharedResourceGroupName: sharedResourceGroupName
    registryName: registryName
    pullIdentityName: pullIdentityName
    frontendImage: frontendImage
    publicIngress: true
    publicJwks: publicJwks
  }
  dependsOn: [api]
}

output applicationResourceGroup string = appResourceGroup.name
output environmentName string = environment.outputs.environmentName
output publicFrontendName string = frontend.outputs.frontendName

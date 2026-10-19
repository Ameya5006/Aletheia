targetScope = 'resourceGroup'

param location string = resourceGroup().location
param serverName string = 'pg-aletheia-sea-1017'
param administratorLogin string = 'aletheia_admin'
@secure()
param administratorPassword string

resource server 'Microsoft.DBforPostgreSQL/flexibleServers@2025-08-01' = {
  name: serverName
  location: location
  tags: {
    project: 'aletheia'
    workload: 'student-showcase'
    costBoundary: 'free-allowances-only'
    dataClass: 'non-sensitive-showcase'
  }
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    createMode: 'Create'
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    // Match the approved local PG18 MLflow metadata archive for byte-faithful restore.
    version: '18'
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
    storage: {
      storageSizeGB: 32
      autoGrow: 'Disabled'
    }
  }
}

// Narrow supervisor exception for this non-sensitive showcase. PostgreSQL
// interprets 0.0.0.0/0.0.0.0 as Azure services, not all internet clients.
resource azureServices 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  parent: server
  name: 'AllowAzureServicesShowcase'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource requireTls 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2024-08-01' = {
  parent: server
  name: 'require_secure_transport'
  properties: {
    value: 'ON'
    source: 'user-override'
  }
}

output serverName string = server.name
output serverFqdn string = server.properties.fullyQualifiedDomainName

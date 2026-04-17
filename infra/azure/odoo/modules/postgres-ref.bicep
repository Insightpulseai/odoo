param postgresServerName string

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' existing = {
  name: postgresServerName
}

output fqdn string = postgres.properties.fullyQualifiedDomainName
output id string = postgres.id

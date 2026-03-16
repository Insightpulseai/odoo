'use client'

import {
  Card,
  Text,
  Switch,
  Divider,
  Input,
  Label,
  Badge,
  Spinner,
  makeStyles,
  tokens,
} from '@fluentui/react-components'
import {
  Settings24Regular,
  Key24Regular,
  Globe24Regular,
  Server24Regular,
  Cloud24Regular,
  ShieldCheckmark24Regular,
  Document24Regular,
  Database24Regular,
} from '@fluentui/react-icons'
import { useDeployments, useKnowledgeBases } from '@/lib/hooks'

const useStyles = makeStyles({
  page: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    maxWidth: '720px',
  },
  sectionCard: {
    padding: '24px',
    borderRadius: '12px',
  },
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '16px',
  },
  sectionIcon: {
    color: '#7B2FF2',
  },
  fieldRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 0',
  },
  fieldLabel: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  inputRow: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    padding: '8px 0',
  },
  readOnly: {
    color: tokens.colorNeutralForeground3,
  },
  policyRow: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    padding: '10px 0',
  },
  policyHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  policyMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginTop: '2px',
  },
  contractRow: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    padding: '10px 0',
  },
  contractStats: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginTop: '4px',
  },
  registryRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '10px 0',
  },
  registryInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  mono: {
    fontFamily: 'monospace',
    fontSize: '12px',
  },
  emptyState: {
    padding: '16px 0',
    textAlign: 'center' as const,
  },
})

interface MsCloudEnvVar {
  name: string
  configured: boolean
}

const msCloudEnvVars: MsCloudEnvVar[] = [
  { name: 'MSCLOUD_TENANT_ID', configured: typeof process !== 'undefined' },
  { name: 'MSCLOUD_CLIENT_ID', configured: typeof process !== 'undefined' },
]

const registrySources = [
  { family: 'Organization Policies', path: 'ssot/org/', source: 'registry' },
  { family: 'Platform Registries', path: 'ops-platform/ssot/', source: 'registry' },
  { family: 'Agent Manifests', path: 'agents/foundry/', source: 'registry' },
  { family: 'Odoo Contracts', path: 'odoo/ssot/odoo/', source: 'registry' },
]

export default function SettingsPage() {
  const styles = useStyles()
  const { policies: deploymentPolicies, isLoading: deploymentsLoading } = useDeployments()
  const { boundaryContracts, policies: kbPolicies, isLoading: kbLoading } = useKnowledgeBases()

  return (
    <div className={styles.page}>
      <div>
        <Text as="h1" size={800} weight="bold">
          Settings
        </Text>
        <Text size={300} style={{ color: tokens.colorNeutralForeground3, marginTop: 4, display: 'block' }}>
          Console configuration and environment
        </Text>
      </div>

      <Card className={styles.sectionCard}>
        <div className={styles.sectionHeader}>
          <Globe24Regular className={styles.sectionIcon} />
          <Text weight="semibold" size={400}>Environment</Text>
        </div>
        <div className={styles.fieldRow}>
          <div className={styles.fieldLabel}>
            <Text weight="semibold">Current Environment</Text>
            <Text size={200} className={styles.readOnly}>Azure Container Apps region</Text>
          </div>
          <Badge appearance="filled" color="informative">dev</Badge>
        </div>
        <Divider />
        <div className={styles.fieldRow}>
          <div className={styles.fieldLabel}>
            <Text weight="semibold">Platform</Text>
            <Text size={200} className={styles.readOnly}>Hosting infrastructure</Text>
          </div>
          <Text className={styles.readOnly}>Azure (southeastasia)</Text>
        </div>
      </Card>

      <Card className={styles.sectionCard}>
        <div className={styles.sectionHeader}>
          <Server24Regular className={styles.sectionIcon} />
          <Text weight="semibold" size={400}>Services</Text>
        </div>
        <div className={styles.fieldRow}>
          <div className={styles.fieldLabel}>
            <Text weight="semibold">Auto-refresh interval</Text>
            <Text size={200} className={styles.readOnly}>Dashboard data polling</Text>
          </div>
          <Text className={styles.readOnly}>30s (coming soon)</Text>
        </div>
        <Divider />
        <div className={styles.fieldRow}>
          <div className={styles.fieldLabel}>
            <Text weight="semibold">Enable notifications</Text>
            <Text size={200} className={styles.readOnly}>Blocker and health alerts</Text>
          </div>
          <Switch disabled aria-label="Enable notifications" />
        </div>
      </Card>

      <Card className={styles.sectionCard}>
        <div className={styles.sectionHeader}>
          <Key24Regular className={styles.sectionIcon} />
          <Text weight="semibold" size={400}>API Configuration</Text>
        </div>
        <div className={styles.inputRow}>
          <Label htmlFor="odoo-url">Odoo Base URL</Label>
          <Input id="odoo-url" value="https://erp.insightpulseai.com" readOnly />
        </div>
        <div className={styles.inputRow}>
          <Label htmlFor="foundry-endpoint">Foundry Endpoint</Label>
          <Input id="foundry-endpoint" placeholder="Set via AZURE_FOUNDRY_ENDPOINT env var" readOnly />
        </div>
      </Card>

      {/* Governance Policies */}
      <Card className={styles.sectionCard}>
        <div className={styles.sectionHeader}>
          <ShieldCheckmark24Regular className={styles.sectionIcon} />
          <Text weight="semibold" size={400}>Governance Policies</Text>
        </div>
        {deploymentsLoading ? (
          <div className={styles.emptyState}>
            <Spinner size="small" label="Loading policies..." />
          </div>
        ) : deploymentPolicies.length === 0 ? (
          <div className={styles.emptyState}>
            <Text className={styles.readOnly}>No governance policies loaded</Text>
          </div>
        ) : (
          deploymentPolicies.map((policy, idx) => (
            <div key={`${policy.name}-${idx}`}>
              {idx > 0 && <Divider />}
              <div className={styles.policyRow}>
                <div className={styles.policyHeader}>
                  <Text weight="semibold">{policy.name}</Text>
                  <Badge appearance="tint" color="informative">{policy.kind}</Badge>
                </div>
                <div className={styles.policyMeta}>
                  <Text size={200} className={styles.readOnly}>v{policy.version}</Text>
                  <Text size={200} className={styles.mono}>{policy.sourceFile}</Text>
                </div>
              </div>
            </div>
          ))
        )}
      </Card>

      {/* Odoo Boundary Contracts */}
      <Card className={styles.sectionCard}>
        <div className={styles.sectionHeader}>
          <Document24Regular className={styles.sectionIcon} />
          <Text weight="semibold" size={400}>Odoo Boundary Contracts</Text>
        </div>
        {kbLoading ? (
          <div className={styles.emptyState}>
            <Spinner size="small" label="Loading contracts..." />
          </div>
        ) : boundaryContracts.length === 0 ? (
          <div className={styles.emptyState}>
            <Text className={styles.readOnly}>No boundary contracts loaded</Text>
          </div>
        ) : (
          boundaryContracts.map((contract, idx) => (
            <div key={`${contract.name}-${idx}`}>
              {idx > 0 && <Divider />}
              <div className={styles.contractRow}>
                <div className={styles.policyHeader}>
                  <Text weight="semibold">{contract.name}</Text>
                  <Badge appearance="tint" color="informative">{contract.kind}</Badge>
                </div>
                {contract.odooModel && (
                  <Text size={200} className={styles.mono}>{contract.odooModel}</Text>
                )}
                <Text size={200} className={styles.readOnly}>{contract.description}</Text>
                <div className={styles.contractStats}>
                  <Badge appearance="tint" color="success">{contract.readOps} read</Badge>
                  <Badge appearance="tint" color="warning">{contract.writeOps} write</Badge>
                  <Badge appearance="tint" color="danger">{contract.prohibited} prohibited</Badge>
                </div>
              </div>
            </div>
          ))
        )}
      </Card>

      <Card className={styles.sectionCard}>
        <div className={styles.sectionHeader}>
          <Cloud24Regular className={styles.sectionIcon} />
          <Text weight="semibold" size={400}>Microsoft Cloud</Text>
        </div>
        {msCloudEnvVars.map((envVar) => (
          <div key={envVar.name}>
            <div className={styles.fieldRow}>
              <div className={styles.fieldLabel}>
                <Text weight="semibold">{envVar.name}</Text>
                <Text size={200} className={styles.readOnly}>
                  Environment variable for Microsoft Cloud integration
                </Text>
              </div>
              <Badge
                appearance="filled"
                color={envVar.configured ? 'success' : 'danger'}
              >
                {envVar.configured ? 'Configured' : 'Not configured'}
              </Badge>
            </div>
            <Divider />
          </div>
        ))}
        <div className={styles.fieldRow}>
          <div className={styles.fieldLabel}>
            <Text weight="semibold">Provider Status</Text>
            <Text size={200} className={styles.readOnly}>Microsoft Cloud data source mode</Text>
          </div>
          <Badge appearance="filled" color="informative">fixture</Badge>
        </div>
      </Card>

      {/* Registry Sources */}
      <Card className={styles.sectionCard}>
        <div className={styles.sectionHeader}>
          <Database24Regular className={styles.sectionIcon} />
          <Text weight="semibold" size={400}>Registry Sources</Text>
        </div>
        {registrySources.map((reg, idx) => (
          <div key={reg.family}>
            {idx > 0 && <Divider />}
            <div className={styles.registryRow}>
              <div className={styles.registryInfo}>
                <Text weight="semibold">{reg.family}</Text>
                <Text size={200} className={styles.mono}>{reg.path}</Text>
              </div>
              <Badge appearance="filled" color="success">{reg.source}</Badge>
            </div>
          </div>
        ))}
      </Card>
    </div>
  )
}

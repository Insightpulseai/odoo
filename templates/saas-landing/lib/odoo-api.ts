/**
 * Odoo JSON-RPC API Client
 * Connects Next.js frontend to Odoo backend
 */

const ODOO_URL = process.env.NEXT_PUBLIC_ODOO_URL || 'https://erp.insightpulseai.com'
const ODOO_DB = process.env.NEXT_PUBLIC_ODOO_DB || 'odoo'

interface OdooRPCRequest {
  jsonrpc: string
  method: string
  params: Record<string, any>
  id?: number
}

interface OdooRPCResponse<T> {
  jsonrpc: string
  id?: number
  result?: T
  error?: {
    code: number
    message: string
    data: any
  }
}

/**
 * Make JSON-RPC call to Odoo
 */
async function callOdoo<T>(
  endpoint: string,
  params: Record<string, any> = {}
): Promise<T> {
  const request: OdooRPCRequest = {
    jsonrpc: '2.0',
    method: 'call',
    params: {
      db: ODOO_DB,
      ...params
    },
    id: Math.floor(Math.random() * 1000000)
  }

  const response = await fetch(`${ODOO_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
    // Don't cache API calls
    cache: 'no-store'
  })

  if (!response.ok) {
    throw new Error(`Odoo API error: ${response.statusText}`)
  }

  const data: OdooRPCResponse<T> = await response.json()

  if (data.error) {
    throw new Error(`Odoo RPC error: ${data.error.message}`)
  }

  return data.result as T
}

/**
 * Authenticate with Odoo
 */
export async function authenticateOdoo(
  username: string,
  password: string
): Promise<{ uid: number; session_id: string }> {
  return callOdoo('/web/session/authenticate', {
    db: ODOO_DB,
    login: username,
    password: password
  })
}

/**
 * Fetch platform features from Odoo CMS
 */
export interface PlatformFeature {
  id: number
  title: string
  description: string
  icon: string
  category: string
  published: boolean
}

export async function fetchPlatformFeatures(): Promise<PlatformFeature[]> {
  try {
    return await callOdoo<PlatformFeature[]>('/api/platform/features', {})
  } catch (error) {
    console.error('Failed to fetch features:', error)
    // Return mock data as fallback
    return [
      {
        id: 1,
        title: 'Instant Deployment',
        description: 'Deploy your changes in seconds',
        icon: '⚡',
        category: 'deployment',
        published: true
      },
      {
        id: 2,
        title: 'Staging Environments',
        description: 'Test before you deploy',
        icon: '🔄',
        category: 'testing',
        published: true
      },
      {
        id: 3,
        title: 'Real-time Monitoring',
        description: 'Track your application health',
        icon: '📊',
        category: 'monitoring',
        published: true
      }
    ]
  }
}

/**
 * Fetch deployments from Odoo
 */
export interface Deployment {
  id: number
  branch: string
  environment: string
  status: 'pending' | 'in_progress' | 'success' | 'failed'
  commit_hash: string
  commit_message: string
  started_at: string
  completed_at?: string
  logs?: string[]
}

export async function fetchDeployments(): Promise<Deployment[]> {
  try {
    return await callOdoo<Deployment[]>('/api/platform/deployments', {})
  } catch (error) {
    console.error('Failed to fetch deployments:', error)
    return []
  }
}

/**
 * Trigger new deployment
 */
export async function triggerDeployment(
  branch: string,
  environment: string
): Promise<{ deployment_id: number; status: string }> {
  return callOdoo('/api/platform/deploy', {
    branch,
    environment
  })
}

/**
 * Fetch build logs
 */
export interface BuildLog {
  timestamp: string
  level: 'info' | 'warn' | 'error' | 'success'
  message: string
}

export async function fetchBuildLogs(deploymentId: number): Promise<BuildLog[]> {
  try {
    return await callOdoo<BuildLog[]>('/api/platform/logs', {
      deployment_id: deploymentId
    })
  } catch (error) {
    console.error('Failed to fetch logs:', error)
    // Return mock logs
    return [
      { timestamp: new Date().toISOString(), level: 'info', message: 'Deployment started' },
      { timestamp: new Date().toISOString(), level: 'info', message: 'Building Docker image...' },
      { timestamp: new Date().toISOString(), level: 'success', message: 'Build completed' }
    ]
  }
}

/**
 * Fetch monitoring metrics
 */
export interface Metrics {
  cpu_usage: number
  memory_usage: number
  response_time: number
  requests_per_minute: number
  error_rate: number
}

export async function fetchMetrics(environment: string): Promise<Metrics> {
  try {
    return await callOdoo<Metrics>('/api/platform/metrics', {
      environment
    })
  } catch (error) {
    console.error('Failed to fetch metrics:', error)
    // Return mock metrics
    return {
      cpu_usage: 24,
      memory_usage: 1.2,
      response_time: 142,
      requests_per_minute: 1234,
      error_rate: 0.01
    }
  }
}

/**
 * Execute command in web shell
 */
export async function executeShellCommand(
  environment: string,
  command: string
): Promise<{ output: string; exit_code: number }> {
  return callOdoo('/api/platform/shell/execute', {
    environment,
    command
  })
}

/**
 * Fetch pricing plans from Odoo product catalog
 */
export interface PricingPlan {
  id: number
  name: string
  description: string
  price: number
  currency: string
  features: string[]
  popular: boolean
}

export async function fetchPricingPlans(): Promise<PricingPlan[]> {
  try {
    return await callOdoo<PricingPlan[]>('/api/platform/pricing', {})
  } catch (error) {
    console.error('Failed to fetch pricing:', error)
    return []
  }
}

/**
 * Fetch blog posts from Odoo website module
 */
export interface BlogPost {
  id: number
  title: string
  subtitle: string
  content: string
  author: string
  published_date: string
  cover_image?: string
  tags: string[]
}

export async function fetchBlogPosts(limit = 10): Promise<BlogPost[]> {
  try {
    return await callOdoo<BlogPost[]>('/website/blog/posts', {
      limit
    })
  } catch (error) {
    console.error('Failed to fetch blog posts:', error)
    return []
  }
}

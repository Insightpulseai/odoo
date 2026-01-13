// =============================================================================
// Multi-Tenant Provider TypeScript Types
// =============================================================================
// Ideal multi-tenant model where:
// - Tenant = organization using the platform
// - Provider = organization offering services/agents to other tenants
// - Same org can be BOTH tenant and provider
//
// Generated: 2026-01-12
// =============================================================================

// =============================================================================
// ENUMS
// =============================================================================

export enum AccountRoleType {
  TENANT = "TENANT",
  PROVIDER = "PROVIDER",
  INTERNAL = "INTERNAL",
}

export enum SubscriptionStatus {
  DRAFT = "DRAFT",
  ACTIVE = "ACTIVE",
  SUSPENDED = "SUSPENDED",
  CANCELLED = "CANCELLED",
}

export enum EnvironmentType {
  DEV = "DEV",
  STAGING = "STAGING",
  PROD = "PROD",
}

export enum AccountLinkType {
  PROVIDER_OF = "PROVIDER_OF",
  RESELLER_OF = "RESELLER_OF",
  PARTNER_OF = "PARTNER_OF",
}

// =============================================================================
// CORE TYPES
// =============================================================================

/**
 * Accounts represent organizations. Can be tenant, provider, or both.
 * Maps to Odoo res.company/res.partner.
 */
export interface Account {
  id: string;
  slug: string;
  name: string;
  legalName?: string | null;
  country?: string | null;
  timezone?: string | null;
  isActive: boolean;
  defaultLocale?: string | null;
  billingEmail?: string | null;
  odooCompanyId?: number | null;
  odooPartnerId?: number | null;
  createdAt: Date;
  updatedAt: Date;
  deletedAt?: Date | null;
}

/**
 * Account role assignment. Accounts can have multiple roles.
 */
export interface AccountRole {
  id: string;
  accountId: string;
  role: AccountRoleType;
  isPrimary: boolean;
  grantedAt: Date;
  grantedBy?: string | null;
}

/**
 * Users belong to one primary account.
 * Maps to Odoo res.users and Supabase auth.users.
 */
export interface User {
  id: string;
  accountId: string;
  email: string;
  fullName?: string | null;
  isAdmin: boolean;
  isActive: boolean;
  authUserId?: string | null;
  odooUserId?: number | null;
  keycloakId?: string | null;
  createdAt: Date;
  updatedAt: Date;
  deletedAt?: Date | null;
}

// =============================================================================
// PROVIDER TYPES
// =============================================================================

/**
 * Services offered by providers.
 */
export interface Service {
  id: string;
  providerAccountId: string;
  key: string;
  name: string;
  description?: string | null;
  isPublic: boolean;
  isEnabled: boolean;
  category?: string | null;
  defaultEnvironmentType?: EnvironmentType | null;
  mcpServerName?: string | null;
  n8nWorkflowId?: string | null;
  createdAt: Date;
  updatedAt: Date;
  deletedAt?: Date | null;
}

/**
 * Pricing plans for services.
 */
export interface ServicePlan {
  id: string;
  serviceId: string;
  key: string;
  name: string;
  description?: string | null;
  monthlyPriceCents?: number | null;
  annualPriceCents?: number | null;
  currency?: string | null;
  maxSeats?: number | null;
  maxRequestsMonth?: number | null;
  featureFlags: Record<string, unknown>;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// =============================================================================
// TENANT TYPES
// =============================================================================

/**
 * Links tenants to provider services. The core billing relationship.
 */
export interface Subscription {
  id: string;
  tenantAccountId: string;
  providerAccountId: string;
  serviceId: string;
  servicePlanId?: string | null;
  status: SubscriptionStatus;
  startedAt?: Date | null;
  endedAt?: Date | null;
  trialEndsAt?: Date | null;
  nextBillingAt?: Date | null;
  externalRef?: string | null;
  billingMetadata: Record<string, unknown>;
  createdAt: Date;
  updatedAt: Date;
  cancelledAt?: Date | null;
}

/**
 * Explicit relationships between accounts.
 */
export interface AccountLink {
  id: string;
  fromAccountId: string;
  toAccountId: string;
  linkType: AccountLinkType;
  metadata: Record<string, unknown>;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// =============================================================================
// ENVIRONMENT TYPES
// =============================================================================

/**
 * Maps accounts to infrastructure bindings.
 */
export interface Environment {
  id: string;
  accountId: string;
  envType: EnvironmentType;
  supabaseProjectRef?: string | null;
  supabaseServiceRole?: string | null;
  vercelProjectId?: string | null;
  vercelTeamId?: string | null;
  digitaloceanAppId?: string | null;
  digitaloceanCluster?: string | null;
  odooDbName?: string | null;
  odooBaseUrl?: string | null;
  supersetDatabaseKey?: string | null;
  supersetDashboardIds?: string[] | null;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// =============================================================================
// USAGE & AUDIT TYPES
// =============================================================================

/**
 * Tracks service usage for billing and limit enforcement.
 */
export interface UsageRecord {
  id: string;
  subscriptionId: string;
  tenantAccountId: string;
  serviceId: string;
  periodStart: Date;
  periodEnd: Date;
  requestCount: number;
  tokenCount: number;
  storageBytes: bigint;
  computeSeconds: number;
  isBilled: boolean;
  billedAt?: Date | null;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Audit trail for account-related changes.
 */
export interface AccountAudit {
  id: string;
  accountId: string;
  actorUserId?: string | null;
  action: string;
  entityType: string;
  entityId: string;
  changes?: Record<string, unknown> | null;
  ipAddress?: string | null;
  userAgent?: string | null;
  createdAt: Date;
}

// =============================================================================
// EXTENDED TYPES WITH RELATIONS
// =============================================================================

/**
 * Account with all relations loaded.
 */
export interface AccountWithRelations extends Account {
  roles: AccountRole[];
  users: User[];
  providedServices: Service[];
  tenantSubscriptions: Subscription[];
  providerSubscriptions: Subscription[];
  environments: Environment[];
}

/**
 * Service with provider and plans loaded.
 */
export interface ServiceWithRelations extends Service {
  providerAccount: Account;
  plans: ServicePlan[];
  subscriptions: Subscription[];
}

/**
 * Subscription with all parties loaded.
 */
export interface SubscriptionWithRelations extends Subscription {
  tenantAccount: Account;
  providerAccount: Account;
  service: Service;
  servicePlan?: ServicePlan | null;
}

// =============================================================================
// INPUT TYPES (FOR CREATE/UPDATE)
// =============================================================================

export interface CreateAccountInput {
  slug: string;
  name: string;
  legalName?: string;
  country?: string;
  timezone?: string;
  defaultLocale?: string;
  billingEmail?: string;
  odooCompanyId?: number;
  odooPartnerId?: number;
}

export interface UpdateAccountInput {
  name?: string;
  legalName?: string;
  country?: string;
  timezone?: string;
  isActive?: boolean;
  defaultLocale?: string;
  billingEmail?: string;
  odooCompanyId?: number;
  odooPartnerId?: number;
}

export interface CreateServiceInput {
  key: string;
  name: string;
  description?: string;
  isPublic?: boolean;
  category?: string;
  defaultEnvironmentType?: EnvironmentType;
  mcpServerName?: string;
  n8nWorkflowId?: string;
}

export interface CreateSubscriptionInput {
  tenantAccountId: string;
  serviceId: string;
  servicePlanId?: string;
  trialEndsAt?: Date;
  externalRef?: string;
}

export interface CreateEnvironmentInput {
  envType: EnvironmentType;
  supabaseProjectRef?: string;
  vercelProjectId?: string;
  vercelTeamId?: string;
  digitaloceanAppId?: string;
  digitaloceanCluster?: string;
  odooDbName?: string;
  odooBaseUrl?: string;
  supersetDatabaseKey?: string;
  supersetDashboardIds?: string[];
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

/**
 * Check if an account has a specific role.
 */
export function hasRole(
  account: AccountWithRelations,
  role: AccountRoleType
): boolean {
  return account.roles.some((r) => r.role === role);
}

/**
 * Check if an account is a provider.
 */
export function isProvider(account: AccountWithRelations): boolean {
  return hasRole(account, AccountRoleType.PROVIDER);
}

/**
 * Check if an account is a tenant.
 */
export function isTenant(account: AccountWithRelations): boolean {
  return hasRole(account, AccountRoleType.TENANT);
}

/**
 * Get active subscriptions for a tenant.
 */
export function getActiveSubscriptions(
  account: AccountWithRelations
): Subscription[] {
  return account.tenantSubscriptions.filter(
    (s) => s.status === SubscriptionStatus.ACTIVE
  );
}

/**
 * Get environment by type.
 */
export function getEnvironment(
  account: AccountWithRelations,
  envType: EnvironmentType
): Environment | undefined {
  return account.environments.find((e) => e.envType === envType && e.isActive);
}

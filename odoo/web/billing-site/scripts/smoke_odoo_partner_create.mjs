#!/usr/bin/env node

/**
 * Smoke test for Odoo partner creation
 *
 * Usage:
 *   ODOO_BASE_URL=https://erp.example.com \
 *   ODOO_DB=odoo_core \
 *   ODOO_USER=api@example.com \
 *   ODOO_PASSWORD=secret \
 *   node scripts/smoke_odoo_partner_create.mjs
 */

import crypto from 'crypto'

const config = {
  baseUrl: process.env.ODOO_BASE_URL,
  db: process.env.ODOO_DB,
  username: process.env.ODOO_USER,
  password: process.env.ODOO_PASSWORD,
}

async function jsonRpc(url, service, method, args) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'call',
      params: {
        service,
        method,
        args,
      },
    }),
  })

  const data = await response.json()

  if (data.error) {
    throw new Error(`Odoo RPC Error: ${data.error.data?.message || data.error.message}`)
  }

  return data.result
}

async function main() {
  console.log('=== Odoo Partner Creation Smoke Test ===\n')

  // Validate configuration
  if (!config.baseUrl || !config.db || !config.username || !config.password) {
    console.error('Missing required environment variables:')
    console.error('  ODOO_BASE_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD')
    process.exit(1)
  }

  console.log(`Odoo URL: ${config.baseUrl}`)
  console.log(`Database: ${config.db}`)
  console.log(`User: ${config.username}\n`)

  try {
    // Step 1: Authenticate
    console.log('1. Authenticating...')
    const uid = await jsonRpc(
      `${config.baseUrl}/jsonrpc`,
      'common',
      'authenticate',
      [config.db, config.username, config.password, {}]
    )

    if (!uid) {
      throw new Error('Authentication failed - check credentials')
    }
    console.log(`   ✓ Authenticated as UID: ${uid}\n`)

    // Step 2: Create test partner
    const testOrgId = crypto.randomUUID()
    const testEmail = `smoke-test-${Date.now()}@example.com`

    console.log('2. Creating test partner...')
    console.log(`   Email: ${testEmail}`)
    console.log(`   Org ID: ${testOrgId}`)

    const partnerId = await jsonRpc(
      `${config.baseUrl}/jsonrpc`,
      'object',
      'execute_kw',
      [
        config.db,
        uid,
        config.password,
        'res.partner',
        'create',
        [
          {
            name: 'Smoke Test Partner',
            email: testEmail,
            is_company: false,
            x_supabase_org_id: testOrgId,
            x_paddle_customer_id: 'ctm_smoke_test',
            customer_rank: 1,
          },
        ],
      ]
    )

    console.log(`   ✓ Created partner ID: ${partnerId}\n`)

    // Step 3: Read back to verify
    console.log('3. Verifying partner...')
    const [partner] = await jsonRpc(
      `${config.baseUrl}/jsonrpc`,
      'object',
      'execute_kw',
      [
        config.db,
        uid,
        config.password,
        'res.partner',
        'read',
        [[partnerId]],
        { fields: ['name', 'email', 'x_supabase_org_id'] },
      ]
    )

    if (partner.x_supabase_org_id !== testOrgId) {
      throw new Error('Partner data mismatch')
    }
    console.log(`   ✓ Partner verified: ${partner.name} (${partner.email})\n`)

    // Step 4: Cleanup - delete test partner
    console.log('4. Cleaning up...')
    await jsonRpc(
      `${config.baseUrl}/jsonrpc`,
      'object',
      'execute_kw',
      [
        config.db,
        uid,
        config.password,
        'res.partner',
        'unlink',
        [[partnerId]],
      ]
    )
    console.log(`   ✓ Test partner deleted\n`)

    console.log('=== SMOKE TEST PASSED ===')
    process.exit(0)
  } catch (error) {
    console.error(`\n❌ SMOKE TEST FAILED: ${error.message}`)
    process.exit(1)
  }
}

main()

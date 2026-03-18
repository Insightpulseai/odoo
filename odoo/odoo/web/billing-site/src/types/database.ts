export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  billing: {
    Tables: {
      customers: {
        Row: {
          id: string
          paddle_customer_id: string
          supabase_user_id: string | null
          email: string
          name: string | null
          company_name: string | null
          country_code: string | null
          vat_number: string | null
          odoo_partner_id: number | null
          metadata: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          paddle_customer_id: string
          supabase_user_id?: string | null
          email: string
          name?: string | null
          company_name?: string | null
          country_code?: string | null
          vat_number?: string | null
          odoo_partner_id?: number | null
          metadata?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          paddle_customer_id?: string
          supabase_user_id?: string | null
          email?: string
          name?: string | null
          company_name?: string | null
          country_code?: string | null
          vat_number?: string | null
          odoo_partner_id?: number | null
          metadata?: Json
          created_at?: string
          updated_at?: string
        }
      }
      subscriptions: {
        Row: {
          id: string
          paddle_subscription_id: string
          customer_id: string
          organization_id: string | null
          status: 'trialing' | 'active' | 'paused' | 'past_due' | 'canceled'
          plan_name: string
          price_id: string
          product_id: string | null
          currency_code: string
          unit_price_amount: number | null
          quantity: number
          billing_cycle_interval: 'day' | 'week' | 'month' | 'year' | null
          billing_cycle_frequency: number
          current_period_start: string | null
          current_period_end: string | null
          canceled_at: string | null
          metadata: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          paddle_subscription_id: string
          customer_id: string
          organization_id?: string | null
          status: 'trialing' | 'active' | 'paused' | 'past_due' | 'canceled'
          plan_name: string
          price_id: string
          product_id?: string | null
          currency_code?: string
          unit_price_amount?: number | null
          quantity?: number
          billing_cycle_interval?: 'day' | 'week' | 'month' | 'year' | null
          billing_cycle_frequency?: number
          current_period_start?: string | null
          current_period_end?: string | null
          canceled_at?: string | null
          metadata?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          paddle_subscription_id?: string
          customer_id?: string
          organization_id?: string | null
          status?: 'trialing' | 'active' | 'paused' | 'past_due' | 'canceled'
          plan_name?: string
          price_id?: string
          product_id?: string | null
          currency_code?: string
          unit_price_amount?: number | null
          quantity?: number
          billing_cycle_interval?: 'day' | 'week' | 'month' | 'year' | null
          billing_cycle_frequency?: number
          current_period_start?: string | null
          current_period_end?: string | null
          canceled_at?: string | null
          metadata?: Json
          created_at?: string
          updated_at?: string
        }
      }
      invoices: {
        Row: {
          id: string
          paddle_invoice_id: string | null
          paddle_transaction_id: string
          customer_id: string
          subscription_id: string | null
          status: 'draft' | 'ready' | 'billed' | 'paid' | 'canceled' | 'past_due'
          currency_code: string
          subtotal: number | null
          tax: number
          total: number
          invoice_number: string | null
          invoice_url: string | null
          billed_at: string | null
          paid_at: string | null
          metadata: Json
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          paddle_invoice_id?: string | null
          paddle_transaction_id: string
          customer_id: string
          subscription_id?: string | null
          status: 'draft' | 'ready' | 'billed' | 'paid' | 'canceled' | 'past_due'
          currency_code?: string
          subtotal?: number | null
          tax?: number
          total: number
          invoice_number?: string | null
          invoice_url?: string | null
          billed_at?: string | null
          paid_at?: string | null
          metadata?: Json
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          paddle_invoice_id?: string | null
          paddle_transaction_id?: string
          customer_id?: string
          subscription_id?: string | null
          status?: 'draft' | 'ready' | 'billed' | 'paid' | 'canceled' | 'past_due'
          currency_code?: string
          subtotal?: number | null
          tax?: number
          total?: number
          invoice_number?: string | null
          invoice_url?: string | null
          billed_at?: string | null
          paid_at?: string | null
          metadata?: Json
          created_at?: string
          updated_at?: string
        }
      }
    }
  }
}

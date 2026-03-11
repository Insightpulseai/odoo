import { createBrowserClient } from '@supabase/ssr'

export type Database = {
  registry: {
    Tables: {
      org_invites: {
        Row: {
          id: string
          org_id: string
          email: string
          role: 'admin' | 'member' | 'viewer'
          token_hash: string
          status: 'pending' | 'accepted' | 'expired' | 'cancelled'
          invited_by: string
          expires_at: string
          accepted_at: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          org_id: string
          email: string
          role: 'admin' | 'member' | 'viewer'
          token_hash: string
          status?: 'pending' | 'accepted' | 'expired' | 'cancelled'
          invited_by: string
          expires_at?: string
          accepted_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          org_id?: string
          email?: string
          role?: 'admin' | 'member' | 'viewer'
          token_hash?: string
          status?: 'pending' | 'accepted' | 'expired' | 'cancelled'
          invited_by?: string
          expires_at?: string
          accepted_at?: string | null
          created_at?: string
          updated_at?: string
        }
      }
    }
    Views: {}
    Functions: {
      create_org_invite_with_token: {
        Args: {
          p_org_id: string
          p_email: string
          p_role: string
          p_token: string
        }
        Returns: Database['registry']['Tables']['org_invites']['Row']
      }
      accept_org_invite: {
        Args: {
          p_token: string
          p_user_id: string
        }
        Returns: {
          org_id: string
          role: string
        }
      }
      cancel_org_invite: {
        Args: {
          p_invite_id: string
        }
        Returns: void
      }
      cleanup_expired_invites: {
        Args: {}
        Returns: number
      }
    }
    Enums: {}
  }
}

export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

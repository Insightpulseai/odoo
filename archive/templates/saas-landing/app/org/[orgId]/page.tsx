"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface Invite {
  id: string
  email: string
  role: string
  status: string
  expires_at: string
  created_at: string
  accepted_at: string | null
}

export default function OrgDashboardPage() {
  const params = useParams()
  const orgId = params.orgId as string

  const [invites, setInvites] = useState<Invite[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Invite form state
  const [inviteEmail, setInviteEmail] = useState("")
  const [inviteRole, setInviteRole] = useState("member")
  const [sendingInvite, setSendingInvite] = useState(false)

  // Fetch invites
  async function fetchInvites() {
    try {
      setLoading(true)
      const res = await fetch(`/api/invite/list?org_id=${orgId}`)

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error || 'Failed to fetch invites')
      }

      const data = await res.json()
      setInvites(data.invites)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load invites')
    } finally {
      setLoading(false)
    }
  }

  // Send invite
  async function handleSendInvite(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    setSendingInvite(true)

    try {
      const res = await fetch('/api/invite/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          org_id: orgId,
          email: inviteEmail,
          role: inviteRole,
          org_name: 'Your Organization' // TODO: Get from org metadata
        })
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error || 'Failed to send invite')
      }

      setSuccess(`Invitation sent to ${inviteEmail}`)
      setInviteEmail("")
      setInviteRole("member")
      fetchInvites() // Refresh list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send invite')
    } finally {
      setSendingInvite(false)
    }
  }

  // Cancel invite
  async function handleCancelInvite(inviteId: string) {
    if (!confirm('Cancel this invitation?')) return

    try {
      const res = await fetch('/api/invite/cancel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ invite_id: inviteId })
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error || 'Failed to cancel invite')
      }

      setSuccess('Invitation cancelled')
      fetchInvites() // Refresh list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel invite')
    }
  }

  // Load invites on mount
  useEffect(() => {
    fetchInvites()
  }, [orgId])

  function getStatusBadge(status: string) {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      pending: "secondary",
      accepted: "default",
      expired: "destructive",
      cancelled: "outline"
    }

    return (
      <Badge variant={variants[status] || "outline"}>
        {status}
      </Badge>
    )
  }

  return (
    <div className="container max-w-5xl mx-auto py-8 px-4 space-y-8">
      {/* Invite Form */}
      <Card>
        <CardHeader>
          <CardTitle>Invite Team Member</CardTitle>
          <CardDescription>
            Send an email invitation to add someone to your organization.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSendInvite} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="email">Email Address *</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="colleague@example.com"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  required
                  disabled={sendingInvite}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Role *</Label>
                <Select value={inviteRole} onValueChange={setInviteRole} disabled={sendingInvite}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="member">Member</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert>
                <AlertDescription>{success}</AlertDescription>
              </Alert>
            )}

            <Button type="submit" disabled={sendingInvite}>
              {sendingInvite ? 'Sending...' : 'Send Invitation'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Invites List */}
      <Card>
        <CardHeader>
          <CardTitle>Team Invitations</CardTitle>
          <CardDescription>
            Manage pending and accepted invitations.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-muted-foreground">Loading invitations...</p>
          ) : invites.length === 0 ? (
            <p className="text-muted-foreground">No invitations yet. Send your first invite above!</p>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Sent</TableHead>
                    <TableHead>Expires</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {invites.map((invite) => (
                    <TableRow key={invite.id}>
                      <TableCell className="font-medium">{invite.email}</TableCell>
                      <TableCell className="capitalize">{invite.role}</TableCell>
                      <TableCell>{getStatusBadge(invite.status)}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {new Date(invite.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {new Date(invite.expires_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        {invite.status === 'pending' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleCancelInvite(invite.id)}
                          >
                            Cancel
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

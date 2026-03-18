"use client"

import { useState, useEffect, Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"

function AcceptInviteContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  // Check auth and redirect if needed
  useEffect(() => {
    // TODO: Check if user is authenticated
    // If not, redirect to login with return URL
    // Example: router.push(`/auth/login?redirect=/invite/accept?token=${token}`)
  }, [])

  async function handleAcceptInvite() {
    if (!token) {
      setError('No invitation token provided')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/invite/accept', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token })
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error || 'Failed to accept invite')
      }

      const { org_id, role } = await res.json()
      setSuccess(true)

      // Redirect to org dashboard after 2 seconds
      setTimeout(() => {
        router.push(`/org/${org_id}`)
      }, 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to accept invite')
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="container max-w-2xl mx-auto py-16 px-4">
        <Card>
          <CardHeader>
            <CardTitle>Invalid Invitation</CardTitle>
          </CardHeader>
          <CardContent>
            <Alert variant="destructive">
              <AlertDescription>
                No invitation token was provided. Please check your invitation email and try again.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container max-w-2xl mx-auto py-16 px-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Organization Invitation</CardTitle>
          <CardDescription>
            You've been invited to join an organization. Accept to get started.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success ? (
            <Alert>
              <AlertDescription className="flex items-center gap-2">
                <span>✓</span>
                <span>Invitation accepted! Redirecting to your organization...</span>
              </AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-4">
              <div className="rounded-lg border p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Invitation Token</span>
                  <Badge variant="secondary">Valid</Badge>
                </div>
                <p className="text-xs text-muted-foreground font-mono break-all">
                  {token.substring(0, 16)}...{token.substring(token.length - 16)}
                </p>
              </div>

              <div className="flex gap-3">
                <Button
                  onClick={handleAcceptInvite}
                  disabled={loading}
                  className="flex-1"
                >
                  {loading ? 'Accepting...' : 'Accept Invitation'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => router.push('/')}
                  disabled={loading}
                >
                  Decline
                </Button>
              </div>

              <p className="text-sm text-muted-foreground text-center">
                By accepting, you'll be added to the organization with the specified role.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default function AcceptInvitePage() {
  return (
    <Suspense fallback={
      <div className="container max-w-2xl mx-auto py-16 px-4">
        <Card>
          <CardHeader>
            <CardTitle>Loading...</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Loading invitation details...</p>
          </CardContent>
        </Card>
      </div>
    }>
      <AcceptInviteContent />
    </Suspense>
  )
}

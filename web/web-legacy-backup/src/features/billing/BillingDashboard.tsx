"use client";

import { Card } from "@/ui/ipai/Card";
import { Button } from "@/ui/ipai/Button";
import { Chip } from "@/ui/ipai/Chip";
import { tokens } from "@ipai/design-tokens";
import { useEffect, useState } from "react";

interface Subscription {
  id: string;
  status: string;
  current_period_end: string;
  plan_name: string;
  price: number;
}

export function BillingDashboard() {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchSubscription() {
      try {
        const res = await fetch("/api/billing/subscription");

        if (res.status === 401) {
          // User not authenticated
          setSubscription(null);
          setLoading(false);
          return;
        }

        if (!res.ok) {
          throw new Error("Failed to fetch subscription");
        }

        const data = await res.json();
        setSubscription(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    fetchSubscription();
  }, []);

  if (loading) {
    return (
      <Card variant="default" className="p-6">
        <p style={{ color: tokens.color.text.secondary }}>Loading billing information...</p>
      </Card>
    );
  }

  if (error) {
    return (
      <Card variant="default" className="p-6">
        <p style={{ color: tokens.color.semantic.error }}>Error: {error}</p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-extrabold" style={{ color: tokens.color.primary }}>
        Billing & Subscription
      </h2>

      {subscription ? (
        <Card variant="default" className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-xl font-bold" style={{ color: tokens.color.text.primary }}>
                {subscription.plan_name}
              </h3>
              <p className="text-2xl font-extrabold mt-2" style={{ color: tokens.color.primary }}>
                ${subscription.price}/month
              </p>
            </div>
            <Chip variant={subscription.status === "active" ? "success" : "default"}>
              {subscription.status}
            </Chip>
          </div>

          <div className="space-y-2 mb-6">
            <p className="text-sm" style={{ color: tokens.color.text.secondary }}>
              <strong>Subscription ID:</strong> {subscription.id}
            </p>
            <p className="text-sm" style={{ color: tokens.color.text.secondary }}>
              <strong>Renews:</strong>{" "}
              {new Date(subscription.current_period_end).toLocaleDateString()}
            </p>
          </div>

          <div className="flex gap-3">
            <Button
              variant="secondary"
              onClick={() => window.open("/billing/manage", "_blank")}
            >
              Manage Subscription
            </Button>
            <Button
              variant="ghost"
              onClick={() => window.open("/billing/invoices", "_blank")}
            >
              View Invoices
            </Button>
          </div>
        </Card>
      ) : (
        <Card variant="default" className="p-6 text-center">
          <p className="mb-4" style={{ color: tokens.color.text.secondary }}>
            You don&apos;t have an active subscription yet.
          </p>
          <Button
            variant="primary"
            onClick={() => (window.location.href = "/pricing")}
          >
            View Plans
          </Button>
        </Card>
      )}
    </div>
  );
}

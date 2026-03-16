"use client";

import { Button } from "@/ui/ipai/Button";
import { Dropdown, DropdownItem } from "@/ui/ipai/Dropdown";
import { OTPLoginModal } from "@/features/auth";
import { tokens } from "@ipai/design-tokens";
import { useState, useEffect } from "react";

interface User {
  id: string;
  email: string;
}

export function Navigation() {
  const [user, setUser] = useState<User | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuth() {
      try {
        const res = await fetch("/api/auth/user");

        if (res.ok) {
          const data = await res.json();
          setUser(data.user);
        }
      } catch (error) {
        console.error("Auth check error:", error);
      } finally {
        setLoading(false);
      }
    }

    checkAuth();
  }, []);

  async function handleSignOut() {
    try {
      await fetch("/api/auth/signout", { method: "POST" });
      setUser(null);
      window.location.reload();
    } catch (error) {
      console.error("Sign out error:", error);
    }
  }

  function handleAuthSuccess() {
    setShowAuthModal(false);
    // Reload to update auth state
    window.location.reload();
  }

  return (
    <>
      <nav
        className="sticky top-0 z-40 border-b"
        style={{
          backgroundColor: tokens.color.surface,
          borderColor: tokens.color.border,
        }}
      >
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span
              className="text-2xl font-extrabold"
              style={{ color: tokens.color.primary }}
            >
              InsightPulse AI
            </span>
          </div>

          <div className="flex items-center space-x-6">
            <a
              href="/features"
              className="font-medium hover:opacity-80 transition-opacity"
              style={{ color: tokens.color.text.primary }}
            >
              Features
            </a>
            <a
              href="/pricing"
              className="font-medium hover:opacity-80 transition-opacity"
              style={{ color: tokens.color.text.primary }}
            >
              Pricing
            </a>
            <a
              href="/docs"
              className="font-medium hover:opacity-80 transition-opacity"
              style={{ color: tokens.color.text.primary }}
            >
              Docs
            </a>

            {loading ? (
              <div className="w-24 h-10 rounded-full animate-pulse" style={{ backgroundColor: tokens.color.canvas }} />
            ) : user ? (
              <Dropdown
                trigger={
                  <Button variant="ghost" size="sm">
                    {user.email}
                  </Button>
                }
                align="right"
              >
                <DropdownItem onClick={() => (window.location.href = "/dashboard")}>
                  Dashboard
                </DropdownItem>
                <DropdownItem onClick={() => (window.location.href = "/billing")}>
                  Billing
                </DropdownItem>
                <DropdownItem onClick={handleSignOut}>Sign Out</DropdownItem>
              </Dropdown>
            ) : (
              <Button variant="primary" size="sm" onClick={() => setShowAuthModal(true)}>
                Sign In
              </Button>
            )}
          </div>
        </div>
      </nav>

      {showAuthModal && (
        <OTPLoginModal onClose={handleAuthSuccess} />
      )}
    </>
  );
}

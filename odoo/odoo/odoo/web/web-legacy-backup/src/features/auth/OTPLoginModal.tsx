import { useState } from "react";
import { Button } from "@/ui/ipai/Button";
import { Card } from "@/ui/ipai/Card";
import { FormField, FormLabel, FormInput, FormMessage } from "@/ui/ipai/Form";
import { tokens } from "@ipai/design-tokens";

export interface OTPLoginModalProps {
  onClose: () => void;
}

export function OTPLoginModal({ onClose }: OTPLoginModalProps) {
  const [step, setStep] = useState<"email" | "verify">("email");
  const [email, setEmail] = useState("");
  const [otp, setOTP] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRequestOTP() {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/auth/otp-request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (res.ok) {
        setStep("verify");
      } else {
        const data = await res.json();
        setError(data.error || "Failed to send OTP code");
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerifyOTP() {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/auth/otp-verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, token: otp }),
      });

      if (res.ok) {
        onClose();
        window.location.reload();  // Reload to update auth state
      } else {
        const data = await res.json();
        setError(data.error || "Invalid OTP code");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: tokens.color.overlay }}
      onClick={onClose}
    >
      <Card
        variant="elevated"
        className="w-full max-w-md p-8"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-2xl font-extrabold mb-6" style={{ color: tokens.color.primary }}>
          {step === "email" ? "Sign In" : "Verify Code"}
        </h2>

        {error && (
          <FormMessage type="error" className="mb-4">
            {error}
          </FormMessage>
        )}

        {step === "email" ? (
          <div className="space-y-4">
            <FormField>
              <FormLabel htmlFor="email">Email Address</FormLabel>
              <FormInput
                id="email"
                type="email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
              />
            </FormField>
            <Button
              variant="primary"
              size="lg"
              className="w-full"
              onClick={handleRequestOTP}
              disabled={loading || !email}
            >
              {loading ? "Sending..." : "Send OTP Code"}
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm mb-4" style={{ color: tokens.color.text.secondary }}>
              Enter the 6-digit code sent to {email}
            </p>
            <FormField>
              <FormLabel htmlFor="otp">Verification Code</FormLabel>
              <FormInput
                id="otp"
                type="text"
                placeholder="000000"
                value={otp}
                onChange={(e) => setOTP(e.target.value.replace(/\D/g, "").slice(0, 6))}
                maxLength={6}
                className="text-center text-2xl tracking-widest"
                disabled={loading}
              />
            </FormField>
            <Button
              variant="primary"
              size="lg"
              className="w-full"
              onClick={handleVerifyOTP}
              disabled={loading || otp.length !== 6}
            >
              {loading ? "Verifying..." : "Verify & Sign In"}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="w-full"
              onClick={() => {
                setStep("email");
                setOTP("");
                setError(null);
              }}
              disabled={loading}
            >
              ← Back to email
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}

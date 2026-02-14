"use client";

import { useState } from "react";
import { tokens } from "@ipai/design-tokens";
import { Button } from "@/ui/ipai/Button";
import { Card } from "@/ui/ipai/Card";
import { Chip } from "@/ui/ipai/Chip";
import { Modal } from "@/ui/ipai/Modal";
import { Dropdown, DropdownItem } from "@/ui/ipai/Dropdown";
import { Form, FormField, FormLabel, FormInput, FormMessage } from "@/ui/ipai/Form";
import { Navigation } from "@/components/Navigation";
import { OTPLoginModal } from "@/features/auth/OTPLoginModal";
import { BillingDashboard } from "@/features/billing/BillingDashboard";

export default function DemoPage() {
  const [showModal, setShowModal] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <>
      <Navigation />
      <main className="min-h-screen py-12" style={{ backgroundColor: tokens.color.bg }}>
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-5xl font-extrabold mb-4" style={{ color: tokens.color.primary }}>
              Platform Kit Component Demo
            </h1>
            <p className="text-xl" style={{ color: tokens.color.text.secondary }}>
              Token-driven design system with Supabase Platform Kit patterns
            </p>
          </div>

          {/* Design Tokens Section */}
          <section>
            <h2 className="text-3xl font-extrabold mb-6" style={{ color: tokens.color.primary }}>
              Design Tokens
            </h2>
            <Card variant="default" className="p-6">
              <h3 className="text-xl font-bold mb-4" style={{ color: tokens.color.text.primary }}>
                Color Palette
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="w-full h-20 rounded-lg mb-2" style={{ backgroundColor: tokens.color.primary }} />
                  <p className="text-sm font-medium">Primary</p>
                  <p className="text-xs" style={{ color: tokens.color.text.secondary }}>
                    {tokens.color.primary}
                  </p>
                </div>
                <div>
                  <div className="w-full h-20 rounded-lg mb-2" style={{ backgroundColor: tokens.color.accent.green }} />
                  <p className="text-sm font-medium">Green</p>
                  <p className="text-xs" style={{ color: tokens.color.text.secondary }}>
                    {tokens.color.accent.green}
                  </p>
                </div>
                <div>
                  <div className="w-full h-20 rounded-lg mb-2" style={{ backgroundColor: tokens.color.accent.teal }} />
                  <p className="text-sm font-medium">Teal</p>
                  <p className="text-xs" style={{ color: tokens.color.text.secondary }}>
                    {tokens.color.accent.teal}
                  </p>
                </div>
                <div>
                  <div className="w-full h-20 rounded-lg mb-2" style={{ backgroundColor: tokens.color.accent.amber }} />
                  <p className="text-sm font-medium">Amber</p>
                  <p className="text-xs" style={{ color: tokens.color.text.secondary }}>
                    {tokens.color.accent.amber}
                  </p>
                </div>
              </div>
            </Card>
          </section>

          {/* Button Section */}
          <section>
            <h2 className="text-3xl font-extrabold mb-6" style={{ color: tokens.color.primary }}>
              Button Component
            </h2>
            <Card variant="default" className="p-6 space-y-6">
              <div>
                <h3 className="text-lg font-bold mb-3" style={{ color: tokens.color.text.primary }}>
                  Variants
                </h3>
                <div className="flex flex-wrap gap-3">
                  <Button variant="primary" size="md">Primary Button</Button>
                  <Button variant="secondary" size="md">Secondary Button</Button>
                  <Button variant="ghost" size="md">Ghost Button</Button>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-bold mb-3" style={{ color: tokens.color.text.primary }}>
                  Sizes
                </h3>
                <div className="flex flex-wrap items-center gap-3">
                  <Button variant="primary" size="sm">Small</Button>
                  <Button variant="primary" size="md">Medium</Button>
                  <Button variant="primary" size="lg">Large</Button>
                </div>
              </div>
            </Card>
          </section>

          {/* Card Section */}
          <section>
            <h2 className="text-3xl font-extrabold mb-6" style={{ color: tokens.color.primary }}>
              Card Component
            </h2>
            <div className="grid md:grid-cols-3 gap-6">
              <Card variant="default" className="p-6">
                <h3 className="text-xl font-bold mb-2" style={{ color: tokens.color.text.primary }}>
                  Default Card
                </h3>
                <p style={{ color: tokens.color.text.secondary }}>
                  Standard card with border and subtle shadow
                </p>
              </Card>
              <Card variant="glass" className="p-6">
                <h3 className="text-xl font-bold mb-2" style={{ color: tokens.color.text.primary }}>
                  Glass Card
                </h3>
                <p style={{ color: tokens.color.text.secondary }}>
                  Glassmorphism effect with backdrop blur
                </p>
              </Card>
              <Card variant="elevated" className="p-6">
                <h3 className="text-xl font-bold mb-2" style={{ color: tokens.color.text.primary }}>
                  Elevated Card
                </h3>
                <p style={{ color: tokens.color.text.secondary }}>
                  Prominent shadow for emphasis
                </p>
              </Card>
            </div>
          </section>

          {/* Chip Section */}
          <section>
            <h2 className="text-3xl font-extrabold mb-6" style={{ color: tokens.color.primary }}>
              Chip Component
            </h2>
            <Card variant="default" className="p-6">
              <div className="flex flex-wrap gap-3">
                <Chip variant="default">Default</Chip>
                <Chip variant="accent">Accent</Chip>
                <Chip variant="success">Success</Chip>
              </div>
            </Card>
          </section>

          {/* Form Section */}
          <section>
            <h2 className="text-3xl font-extrabold mb-6" style={{ color: tokens.color.primary }}>
              Form Components
            </h2>
            <Card variant="default" className="p-6">
              <Form>
                <FormField>
                  <FormLabel>Email Address</FormLabel>
                  <FormInput type="email" placeholder="you@example.com" />
                  <FormMessage type="info">Enter your email to continue</FormMessage>
                </FormField>
                <FormField>
                  <FormLabel>Password</FormLabel>
                  <FormInput type="password" placeholder="••••••••" />
                </FormField>
                <Button variant="primary" size="md" type="submit">
                  Submit Form
                </Button>
              </Form>
            </Card>
          </section>

          {/* Modal Section */}
          <section>
            <h2 className="text-3xl font-extrabold mb-6" style={{ color: tokens.color.primary }}>
              Modal Component
            </h2>
            <Card variant="default" className="p-6">
              <Button variant="primary" size="md" onClick={() => setShowModal(true)}>
                Open Modal
              </Button>
            </Card>
          </section>

          {/* Dropdown Section */}
          <section>
            <h2 className="text-3xl font-extrabold mb-6" style={{ color: tokens.color.primary }}>
              Dropdown Component
            </h2>
            <Card variant="default" className="p-6">
              <Dropdown
                trigger={<Button variant="secondary" size="md">Open Menu</Button>}
                align="left"
              >
                <DropdownItem onClick={() => alert("Profile clicked")}>Profile</DropdownItem>
                <DropdownItem onClick={() => alert("Settings clicked")}>Settings</DropdownItem>
                <DropdownItem onClick={() => alert("Logout clicked")}>Logout</DropdownItem>
              </Dropdown>
            </Card>
          </section>

          {/* Authentication Section */}
          <section>
            <h2 className="text-3xl font-extrabold mb-6" style={{ color: tokens.color.primary }}>
              Authentication (OTP)
            </h2>
            <Card variant="default" className="p-6">
              <p className="mb-4" style={{ color: tokens.color.text.secondary }}>
                Two-step authentication flow with email and OTP verification
              </p>
              <Button variant="primary" size="md" onClick={() => setShowAuthModal(true)}>
                Try OTP Login
              </Button>
            </Card>
          </section>

          {/* Billing Section */}
          <section>
            <h2 className="text-3xl font-extrabold mb-6" style={{ color: tokens.color.primary }}>
              Billing Dashboard
            </h2>
            <BillingDashboard />
          </section>
        </div>
      </main>

      {/* Modals */}
      <Modal open={showModal} onClose={() => setShowModal(false)} title="Demo Modal">
        <div className="space-y-4">
          <p style={{ color: tokens.color.text.primary }}>
            This is a demo modal component with backdrop overlay and click-outside-to-close behavior.
          </p>
          <div className="flex gap-3">
            <Button variant="primary" size="md" onClick={() => setShowModal(false)}>
              Confirm
            </Button>
            <Button variant="ghost" size="md" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
          </div>
        </div>
      </Modal>

      {showAuthModal && <OTPLoginModal onClose={() => setShowAuthModal(false)} />}
    </>
  );
}

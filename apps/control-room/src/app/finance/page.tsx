"use client";

import {
  Button,
  makeStyles,
  shorthands,
  tokens,
} from "@fluentui/react-components";
import { financeAssets } from "@/assets/financeAssets";
import Image from "next/image";

const useStyles = makeStyles({
  page: {
    minHeight: "100vh",
    backgroundColor: tokens.colorNeutralBackground1,
  },

  // Header/Navigation
  header: {
    position: "sticky",
    top: 0,
    zIndex: 1000,
    backgroundColor: "#000000",
    ...shorthands.borderBottom("1px", "solid", "rgba(255, 255, 255, 0.1)"),
  },
  headerContent: {
    maxWidth: "1280px",
    marginLeft: "auto",
    marginRight: "auto",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    ...shorthands.padding("16px", "24px"),
  },
  logo: {
    height: "40px",
    width: "auto",
  },
  nav: {
    display: "flex",
    alignItems: "center",
    ...shorthands.gap("32px"),
    "@media (max-width: 768px)": {
      display: "none",
    },
  },
  navLink: {
    color: "#FFFFFF",
    textDecoration: "none",
    fontSize: "14px",
    fontWeight: 500,
    ":hover": {
      color: "#F1C100",
    },
  },
  loginButton: {
    backgroundColor: "#F1C100",
    color: "#000000",
    fontWeight: 600,
    ":hover": {
      backgroundColor: "#FFD84D",
    },
  },

  // Hero Section
  hero: {
    maxWidth: "1280px",
    marginLeft: "auto",
    marginRight: "auto",
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    alignItems: "center",
    ...shorthands.gap("64px"),
    ...shorthands.padding("120px", "24px"),
    "@media (max-width: 968px)": {
      gridTemplateColumns: "1fr",
      ...shorthands.padding("60px", "24px"),
    },
  },
  heroContent: {
    display: "flex",
    flexDirection: "column",
    ...shorthands.gap("24px"),
  },
  heroTitle: {
    fontSize: "56px",
    fontWeight: 700,
    lineHeight: "1.1",
    color: "#000000",
    ...shorthands.margin(0),
    "@media (max-width: 768px)": {
      fontSize: "40px",
    },
  },
  heroSubtitle: {
    fontSize: "18px",
    lineHeight: "1.6",
    color: "#6B7280",
    ...shorthands.margin(0),
  },
  heroCtas: {
    display: "flex",
    ...shorthands.gap("16px"),
    marginTop: "16px",
    "@media (max-width: 480px)": {
      flexDirection: "column",
    },
  },
  primaryCta: {
    backgroundColor: "#F1C100",
    color: "#000000",
    fontWeight: 600,
    fontSize: "16px",
    ...shorthands.padding("12px", "32px"),
    ":hover": {
      backgroundColor: "#FFD84D",
    },
  },
  secondaryCta: {
    backgroundColor: "transparent",
    color: "#000000",
    fontWeight: 600,
    fontSize: "16px",
    ...shorthands.border("2px", "solid", "#000000"),
    ...shorthands.padding("12px", "32px"),
    ":hover": {
      backgroundColor: "rgba(0, 0, 0, 0.05)",
    },
  },
  heroImage: {
    position: "relative",
    width: "100%",
    height: "500px",
    backgroundColor: "#F5F5F5",
    ...shorthands.borderRadius("16px"),
    ...shorthands.overflow("hidden"),
    boxShadow: "0 8px 32px rgba(0, 0, 0, 0.12)",
    "@media (max-width: 968px)": {
      height: "400px",
    },
  },

  // Features Section
  features: {
    backgroundColor: "#F5F5F5",
    ...shorthands.padding("80px", "24px"),
  },
  featuresContent: {
    maxWidth: "1280px",
    marginLeft: "auto",
    marginRight: "auto",
  },
  featuresTitle: {
    fontSize: "36px",
    fontWeight: 700,
    textAlign: "center",
    color: "#000000",
    marginBottom: "64px",
  },
  featuresGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    ...shorthands.gap("32px"),
    "@media (max-width: 968px)": {
      gridTemplateColumns: "repeat(2, 1fr)",
    },
    "@media (max-width: 480px)": {
      gridTemplateColumns: "1fr",
    },
  },
  featureCard: {
    backgroundColor: "#FFFFFF",
    ...shorthands.borderRadius("12px"),
    ...shorthands.padding("32px", "24px"),
    textAlign: "center",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)",
    ...shorthands.transition("transform", "200ms", "ease"),
    ":hover": {
      transform: "translateY(-4px)",
      boxShadow: "0 4px 16px rgba(0, 0, 0, 0.12)",
    },
  },
  featureIcon: {
    width: "64px",
    height: "64px",
    marginLeft: "auto",
    marginRight: "auto",
    marginBottom: "16px",
  },
  featureTitle: {
    fontSize: "18px",
    fontWeight: 600,
    color: "#000000",
    marginBottom: "8px",
  },
  featureDescription: {
    fontSize: "14px",
    color: "#6B7280",
    lineHeight: "1.5",
  },

  // Integrations Section
  integrations: {
    position: "relative",
    ...shorthands.padding("80px", "24px"),
    ...shorthands.overflow("hidden"),
  },
  integrationsContent: {
    position: "relative",
    zIndex: 1,
    maxWidth: "1280px",
    marginLeft: "auto",
    marginRight: "auto",
  },
  integrationsBg: {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    opacity: 0.03,
    pointerEvents: "none",
  },
  integrationsTitle: {
    fontSize: "36px",
    fontWeight: 700,
    textAlign: "center",
    color: "#000000",
    marginBottom: "48px",
  },
  integrationsList: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    ...shorthands.gap("24px"),
    "@media (max-width: 768px)": {
      gridTemplateColumns: "1fr",
    },
  },
  integrationItem: {
    backgroundColor: "#FFFFFF",
    ...shorthands.borderRadius("8px"),
    ...shorthands.padding("24px"),
    ...shorthands.border("1px", "solid", "rgba(0, 0, 0, 0.1)"),
  },
  integrationName: {
    fontSize: "16px",
    fontWeight: 600,
    color: "#000000",
    marginBottom: "8px",
  },
  integrationDesc: {
    fontSize: "14px",
    color: "#6B7280",
  },

  // Testimonial Section
  testimonial: {
    backgroundColor: "#F5F5F5",
    ...shorthands.padding("80px", "24px"),
  },
  testimonialContent: {
    maxWidth: "800px",
    marginLeft: "auto",
    marginRight: "auto",
    textAlign: "center",
  },
  testimonialCard: {
    backgroundColor: "#FFFFFF",
    ...shorthands.borderRadius("16px"),
    ...shorthands.padding("48px", "40px"),
    boxShadow: "0 4px 16px rgba(0, 0, 0, 0.08)",
  },
  testimonialQuote: {
    fontSize: "20px",
    lineHeight: "1.6",
    color: "#000000",
    fontStyle: "italic",
    marginBottom: "24px",
  },
  testimonialAuthor: {
    fontSize: "14px",
    fontWeight: 600,
    color: "#000000",
    marginBottom: "8px",
  },
  testimonialRole: {
    fontSize: "14px",
    color: "#6B7280",
  },
  testimonialBadge: {
    marginTop: "24px",
    display: "inline-block",
  },

  // Footer
  footer: {
    backgroundColor: "#000000",
    color: "#FFFFFF",
    ...shorthands.padding("60px", "24px", "30px"),
  },
  footerContent: {
    maxWidth: "1280px",
    marginLeft: "auto",
    marginRight: "auto",
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    ...shorthands.gap("48px"),
    marginBottom: "40px",
    "@media (max-width: 768px)": {
      gridTemplateColumns: "repeat(2, 1fr)",
    },
    "@media (max-width: 480px)": {
      gridTemplateColumns: "1fr",
    },
  },
  footerColumn: {
    display: "flex",
    flexDirection: "column",
    ...shorthands.gap("12px"),
  },
  footerTitle: {
    fontSize: "14px",
    fontWeight: 600,
    color: "#F1C100",
    marginBottom: "8px",
  },
  footerLink: {
    fontSize: "14px",
    color: "rgba(255, 255, 255, 0.7)",
    textDecoration: "none",
    ":hover": {
      color: "#FFFFFF",
    },
  },
  footerBottom: {
    ...shorthands.borderTop("1px", "solid", "rgba(255, 255, 255, 0.1)"),
    ...shorthands.padding("20px", "0", "0"),
    textAlign: "center",
    fontSize: "14px",
    color: "rgba(255, 255, 255, 0.5)",
  },
});

export default function FinancePage() {
  const styles = useStyles();

  return (
    <div className={styles.page}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <img
            src={financeAssets.wordmark}
            alt="TBWA"
            className={styles.logo}
          />
          <nav className={styles.nav}>
            <a href="#product" className={styles.navLink}>Product</a>
            <a href="#security" className={styles.navLink}>Security</a>
            <a href="#pricing" className={styles.navLink}>Pricing</a>
            <Button appearance="primary" className={styles.loginButton}>
              Login
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>
            Modernize Your Financial Workflow Without Losing Oversight
          </h1>
          <p className={styles.heroSubtitle}>
            Connect your ERP, analytics, and team chat in one unified workspace.
            Built for finance teams who need real-time visibility, audit trails, and compliance—without the complexity.
          </p>
          <p className={styles.heroSubtitle}>
            No data migration. No months-long implementation. Just seamless integration with the tools you already use.
          </p>
          <div className={styles.heroCtas}>
            <Button appearance="primary" size="large" className={styles.primaryCta}>
              Talk to an Expert
            </Button>
            <Button appearance="outline" size="large" className={styles.secondaryCta}>
              View Demo
            </Button>
          </div>
        </div>
        <div className={styles.heroImage}>
          <Image
            src={financeAssets.hero}
            alt="Finance Workspace Dashboard"
            fill
            style={{ objectFit: "contain" }}
            priority
          />
        </div>
      </section>

      {/* Features Section */}
      <section id="product" className={styles.features}>
        <div className={styles.featuresContent}>
          <h2 className={styles.featuresTitle}>
            Everything You Need in One Platform
          </h2>
          <div className={styles.featuresGrid}>
            <div className={styles.featureCard}>
              <Image
                src={financeAssets.iconErp}
                alt="ERP Integration"
                width={64}
                height={64}
                className={styles.featureIcon}
              />
              <h3 className={styles.featureTitle}>ERP Integration</h3>
              <p className={styles.featureDescription}>
                Connect Odoo, SAP, or custom systems with real-time data sync and automated workflows.
              </p>
            </div>

            <div className={styles.featureCard}>
              <Image
                src={financeAssets.iconAnalytics}
                alt="Live Analytics"
                width={64}
                height={64}
                className={styles.featureIcon}
              />
              <h3 className={styles.featureTitle}>Live Analytics</h3>
              <p className={styles.featureDescription}>
                Real-time dashboards with custom KPIs, automated reports, and drill-down capabilities.
              </p>
            </div>

            <div className={styles.featureCard}>
              <Image
                src={financeAssets.iconChat}
                alt="Team Chat"
                width={64}
                height={64}
                className={styles.featureIcon}
              />
              <h3 className={styles.featureTitle}>Team Chat</h3>
              <p className={styles.featureDescription}>
                Context-aware messaging with transaction threads, approval flows, and audit logs.
              </p>
            </div>

            <div className={styles.featureCard}>
              <Image
                src={financeAssets.iconAudit}
                alt="Audit Trails"
                width={64}
                height={64}
                className={styles.featureIcon}
              />
              <h3 className={styles.featureTitle}>Audit Trails</h3>
              <p className={styles.featureDescription}>
                Complete activity logging, compliance reporting, and immutable transaction history.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section className={styles.integrations}>
        <div className={styles.integrationsBg}>
          <Image
            src={financeAssets.bgGrid}
            alt=""
            fill
            style={{ objectFit: "cover" }}
          />
        </div>
        <div className={styles.integrationsContent}>
          <h2 className={styles.integrationsTitle}>
            Works With Your Existing Stack
          </h2>
          <div className={styles.integrationsList}>
            <div className={styles.integrationItem}>
              <h4 className={styles.integrationName}>Odoo ERP</h4>
              <p className={styles.integrationDesc}>
                Native integration with all Odoo 18 modules, custom fields, and workflows.
              </p>
            </div>
            <div className={styles.integrationItem}>
              <h4 className={styles.integrationName}>Supabase</h4>
              <p className={styles.integrationDesc}>
                Real-time PostgreSQL sync, edge functions, and serverless architecture.
              </p>
            </div>
            <div className={styles.integrationItem}>
              <h4 className={styles.integrationName}>Mattermost</h4>
              <p className={styles.integrationDesc}>
                Secure team messaging with compliance-ready audit logs and retention.
              </p>
            </div>
            <div className={styles.integrationItem}>
              <h4 className={styles.integrationName}>Apache Superset</h4>
              <p className={styles.integrationDesc}>
                Self-service BI with SQL queries, chart builder, and dashboard sharing.
              </p>
            </div>
            <div className={styles.integrationItem}>
              <h4 className={styles.integrationName}>n8n Workflows</h4>
              <p className={styles.integrationDesc}>
                No-code automation for BIR filing, approvals, and multi-agency operations.
              </p>
            </div>
            <div className={styles.integrationItem}>
              <h4 className={styles.integrationName}>DigitalOcean</h4>
              <p className={styles.integrationDesc}>
                App Platform deployment with auto-scaling and managed databases.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonial Section */}
      <section id="security" className={styles.testimonial}>
        <div className={styles.testimonialContent}>
          <div className={styles.testimonialCard}>
            <p className={styles.testimonialQuote}>
              "We reduced month-end closing from 10 days to 3 days. The automated BIR filing alone saved us 40 hours per quarter across 8 agencies."
            </p>
            <p className={styles.testimonialAuthor}>Jake Tolentino</p>
            <p className={styles.testimonialRole}>Finance SSC Manager</p>
            <div className={styles.testimonialBadge}>
              <Image
                src={financeAssets.badgeSecure}
                alt="Audit-Ready & Secure"
                width={240}
                height={64}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerColumn}>
            <h4 className={styles.footerTitle}>Company</h4>
            <a href="#about" className={styles.footerLink}>About</a>
            <a href="#careers" className={styles.footerLink}>Careers</a>
            <a href="#contact" className={styles.footerLink}>Contact</a>
          </div>

          <div className={styles.footerColumn}>
            <h4 className={styles.footerTitle}>Platform</h4>
            <a href="#features" className={styles.footerLink}>Features</a>
            <a href="#integrations" className={styles.footerLink}>Integrations</a>
            <a href="#security" className={styles.footerLink}>Security</a>
          </div>

          <div className={styles.footerColumn}>
            <h4 className={styles.footerTitle}>Documentation</h4>
            <a href="#guides" className={styles.footerLink}>Guides</a>
            <a href="#api" className={styles.footerLink}>API Reference</a>
            <a href="#changelog" className={styles.footerLink}>Changelog</a>
          </div>

          <div className={styles.footerColumn}>
            <h4 className={styles.footerTitle}>Legal</h4>
            <a href="#privacy" className={styles.footerLink}>Privacy Policy</a>
            <a href="#terms" className={styles.footerLink}>Terms of Service</a>
            <a href="#compliance" className={styles.footerLink}>Compliance</a>
          </div>
        </div>

        <div className={styles.footerBottom}>
          © 2026 TBWA Finance Workflow. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

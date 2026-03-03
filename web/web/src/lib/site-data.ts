export const siteData = {
  name: "InsightPulseAI",
  tagline: "Enterprise ERP, Powered by AI",
  description: "Self-hosted Odoo 19 + intelligent automation for Philippine enterprises",

  hero: {
    title: "Enterprise ERP, Powered by AI",
    subtitle: "Self-hosted Odoo 19 with intelligent automation — expense OCR, analytics bridges, and workflow orchestration for Philippine enterprises.",
    primaryCta: { label: "Book a Demo", href: "#contact" },
    secondaryCta: { label: "Explore Modules", href: "#features" },
  },

  features: [
    {
      title: "ERP Core",
      description: "Full Odoo 19 CE with OCA community modules — accounting, HR, inventory, CRM, and project management out of the box.",
      icon: "server",
    },
    {
      title: "Expense OCR",
      description: "Snap a receipt, get a structured expense entry. PaddleOCR-VL extracts vendor, amount, date, and tax with 95%+ accuracy.",
      icon: "scan",
    },
    {
      title: "AI Document Intelligence",
      description: "PaddleOCR-VL processes invoices, receipts, and forms — extracting structured data for automated bookkeeping and compliance.",
      icon: "brain",
    },
    {
      title: "Analytics Bridge",
      description: "Connect Odoo data to Apache Superset and Tableau. Real-time dashboards with preset analytics and one-click data exports.",
      icon: "chart",
    },
    {
      title: "Workflow Automation",
      description: "n8n-powered automation connecting Odoo to Slack, email, OCR services, and 400+ integrations. No-code workflow builder.",
      icon: "workflow",
    },
  ],

  featuresList: [
    {
      title: "Finance & Compliance",
      description: "BIR-compliant tax filing automation (1601-C, 2550Q), multi-agency withholding, and automated monthly/quarterly submissions.",
      details: ["BIR tax automation", "Multi-agency withholding", "Automated submissions", "Audit-ready reports"],
    },
    {
      title: "Human Resources",
      description: "Philippine labor law compliant HR — SSS, PhilHealth, Pag-IBIG integration with automated contribution computation.",
      details: ["SSS/PhilHealth/Pag-IBIG", "Payroll automation", "Leave management", "Employee self-service"],
    },
    {
      title: "Inventory & Supply Chain",
      description: "Real-time stock tracking with barcode scanning, automated reorder points, and multi-warehouse management.",
      details: ["Barcode scanning", "Auto-reorder", "Multi-warehouse", "Delivery tracking"],
    },
  ],

  pricing: [
    {
      name: "Starter",
      description: "For small teams getting started with ERP",
      features: ["Up to 10 users", "Core ERP modules", "Email support", "Monthly backups"],
      cta: "Contact Us",
    },
    {
      name: "Business",
      description: "For growing businesses with automation needs",
      features: ["Up to 50 users", "All modules + OCR", "n8n automation", "Priority support", "Daily backups"],
      cta: "Contact Us",
      highlighted: true,
    },
    {
      name: "Enterprise",
      description: "For organizations requiring full customization",
      features: ["Unlimited users", "Custom modules", "Dedicated support", "SLA guarantee", "On-premise option"],
      cta: "Contact Us",
    },
  ],

  faq: [
    {
      question: "What is InsightPulseAI?",
      answer: "InsightPulseAI is a self-hosted ERP platform built on Odoo 19 Community Edition with AI-powered automation. It combines enterprise resource planning with intelligent document processing, workflow automation, and analytics.",
    },
    {
      question: "Is this BIR-compliant for Philippine businesses?",
      answer: "Yes. Our finance module includes automated BIR tax filing for forms 1601-C and 2550Q, multi-agency withholding tax computation, and audit-ready report generation compliant with Philippine tax regulations.",
    },
    {
      question: "How is data security handled?",
      answer: "Your data stays on your infrastructure. We deploy on DigitalOcean Singapore (SGP1) for low-latency access in the Philippines. All data is encrypted at rest and in transit, with role-based access controls and regular backups.",
    },
    {
      question: "Can I migrate from existing ERP systems?",
      answer: "Yes. We provide migration tools and support for transitioning from legacy systems, spreadsheet-based workflows, and other ERP platforms. Data mapping and validation is included in our onboarding process.",
    },
    {
      question: "What customizations are possible?",
      answer: "InsightPulseAI supports custom Odoo modules (ipai_* namespace), n8n workflow automation for any business process, and API integrations with 400+ third-party services via our automation layer.",
    },
    {
      question: "What support options are available?",
      answer: "We offer email support for Starter plans, priority support with dedicated channels for Business plans, and dedicated account management with SLA guarantees for Enterprise customers.",
    },
  ],

  callout: {
    title: "Ready to modernize your back office?",
    subtitle: "Get a personalized demo of InsightPulseAI for your business.",
    cta: { label: "Book a Demo", href: "#contact" },
  },

  footer: {
    copyright: `\u00A9 ${new Date().getFullYear()} InsightPulseAI. All rights reserved.`,
    links: [
      { label: "GitHub", href: "https://github.com/Insightpulseai" },
      { label: "Documentation", href: "/docs" },
      { label: "Contact", href: "#contact" },
    ],
  },
};

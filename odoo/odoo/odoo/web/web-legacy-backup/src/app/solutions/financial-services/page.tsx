import { Metadata } from 'next';
import { loadSolution } from '@/lib/content';
import {
  SolutionHero,
  LogoStrip,
  Pillars,
  DeploymentOptions,
  UseCases,
  ResourceGrid,
  PartnerStrip,
  FinalCta,
} from '@/components/solutions';

// Load content at build time
function getPageContent() {
  return loadSolution('financial-services');
}

export async function generateMetadata(): Promise<Metadata> {
  const content = getPageContent();

  return {
    title: content.seo?.title || `${content.kicker} Solutions`,
    description: content.seo?.description || content.subtitle,
    keywords: content.seo?.keywords,
    openGraph: {
      title: content.seo?.title || content.title,
      description: content.seo?.description || content.subtitle,
      images: content.seo?.ogImage ? [content.seo.ogImage] : undefined,
    },
  };
}

export default function FinancialServicesSolutionPage() {
  const content = getPageContent();

  return (
    <main>
      {/* Hero Section */}
      <SolutionHero
        kicker={content.kicker}
        title={content.title}
        subtitle={content.subtitle}
        primaryCta={content.primaryCta}
        secondaryCta={content.secondaryCta}
        backgroundImage={content.hero?.backgroundImage}
        heroImages={content.hero?.heroImages}
      />

      {/* Customer Logos */}
      {content.customerLogos && (
        <LogoStrip
          title="Trusted by leading financial institutions"
          logos={content.customerLogos}
        />
      )}

      {/* Feature Pillars */}
      {content.pillars && (
        <Pillars
          title="Built for Regulated Industries"
          subtitle="Every feature designed with security, compliance, and operational efficiency in mind."
          items={content.pillars}
        />
      )}

      {/* Deployment Options */}
      {content.deploymentOptions && (
        <DeploymentOptions
          title={content.deploymentOptions.title}
          items={content.deploymentOptions.items}
        />
      )}

      {/* Use Cases */}
      {content.useCases && (
        <UseCases
          title="Real-World Financial Workflows"
          subtitle="See how leading institutions use our platform to accelerate critical processes."
          items={content.useCases}
        />
      )}

      {/* Resources */}
      {content.resources && (
        <ResourceGrid
          title="Learn More"
          subtitle="Guides, case studies, and best practices for financial services teams."
          items={content.resources}
        />
      )}

      {/* Partners */}
      {content.partners && (
        <PartnerStrip
          title={content.partners.title}
          items={content.partners.items}
        />
      )}

      {/* Final CTA */}
      {content.finalCta && (
        <FinalCta
          title={content.finalCta.title}
          subtitle={content.finalCta.subtitle}
          primaryCta={content.finalCta.primaryCta}
          secondaryCta={content.finalCta.secondaryCta}
        />
      )}
    </main>
  );
}

# Edge Redirect Rules

Redirect rules applied at the Azure Front Door edge layer. Covers domain migrations, vanity URLs, and deprecated path redirects.

## Convention

- Rules defined in YAML, applied via Azure Front Door rules engine
- Each rule must declare: source, target, status code (301/302), reason
- Deprecated domain redirects (e.g., insightpulseai.net) are permanent (301)

<!-- TODO: Codify existing Front Door redirect rules -->

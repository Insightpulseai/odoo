# Image Prompt Library

Versioned prompt templates for Gemini (Nano Banana) and Imagen image generation.

## Provider Routing

| Use Case | Model | Rationale |
|----------|-------|-----------|
| Fast stills, variants, editing | Nano Banana 2 (`gemini-3.1-flash-image-preview`) | Speed, iteration |
| Stable production | Gemini 2.5 Flash Image (`gemini-2.5-flash-image`) | Proven, supports ImageConfig |
| Premium brand-critical | Imagen 4.0 (`imagen-4.0-generate-001`) | Highest quality, native aspect ratio |
| Video | Veo 3.x | Motion, hero films |

## Prompt Formula

```
Subject + Action + Location/Context + Composition + Style
```

## Rules

- Use **positive framing** (describe what you want, not what to avoid)
- Specify **camera/composition** (angle, framing, depth, lighting)
- Put rendered text in **quotes**
- Keep prompts under **480 tokens** for Imagen
- Always specify **aspect ratio** via `ImageConfig`
- Iterate conversationally — don't expect perfection in one shot

## Categories

| Folder | Use Case |
|--------|----------|
| `brand/` | OG cards, keynote covers, architecture diagrams |
| `marketing/` | Homepage heroes, campaign visuals |
| `product-ui/` | Dashboard mockups, UI concepts, approval workflows |
| `ads/` | Ad creatives, social cards |
| `docs-diagrams/` | Architecture visuals, document intelligence |
| `edit-workflows/` | Sketch-to-UI, branding swaps, text rendering |

## References

- [Google Cloud Nano Banana Guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana)
- [Imagen Prompt Guide](https://ai.google.dev/gemini-api/docs/imagen)
- [Awesome Nano Banana](https://github.com/jimmylv/awesome-nano-banana)
- [Gemini Image Prompting Handbook](https://github.com/pauhu/gemini-image-prompting-handbook)

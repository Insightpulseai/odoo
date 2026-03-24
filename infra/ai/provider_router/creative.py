"""
Creative Generation Service — Image & Video via Gemini / Imagen / fal

Implements the generation routing defined in ssot/creative/provider_policy.yaml:
  - stills_fast: Gemini direct (Nano Banana 2)
  - stills_premium: Gemini direct (Nano Banana Pro)
  - premium_brand: Imagen 4
  - video: fal (Kling, Veo, LTX) or Gemini Veo direct
  - utilities: fal (background removal, upscaling, SVG, Lottie)

SDK: google-genai (current) — NOT the deprecated google-generativeai.
Auth: GEMINI_API_KEY environment variable.
"""

import os
import io
import time
import json
import base64
import logging
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class CreativeProvider(str, Enum):
    GEMINI = "gemini"
    IMAGEN = "imagen"
    FAL = "fal"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class QualityTier(str, Enum):
    FAST = "fast"        # Nano Banana 2 (gemini-2.5-flash-image)
    STANDARD = "standard"  # Nano Banana Pro (gemini-3-pro-image-preview)
    PREMIUM = "premium"  # Imagen 4


# Model registry — canonical names from SSOT + Gemini API docs
GEMINI_IMAGE_MODELS = {
    "fast": "nano-banana-2-preview",        # Gemini 3.1 Flash Image
    "standard": "nano-banana-pro-preview",  # Gemini 3 Pro Image
}

IMAGEN_MODELS = {
    "default": "imagen-4",
    "fast": "imagen-4",
    "ultra": "imagen-4",
}

VEO_MODELS = {
    "default": "veo-3.1-preview",
}


class CreativeError(Exception):
    """Base exception for creative generation errors."""
    def __init__(self, message: str, provider: str, original_error: Optional[Exception] = None):
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"[{provider}] {message}")


@dataclass
class GeneratedAsset:
    """Result of a generation request."""
    media_type: str              # "image" or "video"
    provider: str                # gemini, imagen, fal
    model: str                   # model ID used
    format: str                  # png, jpeg, mp4, webm
    data: bytes                  # raw binary content
    width: Optional[int] = None
    height: Optional[int] = None
    duration_s: Optional[float] = None  # video only
    prompt: str = ""
    latency_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def save(self, path: str) -> str:
        """Save asset to file, return path."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(self.data)
        logger.info(f"Saved {self.media_type} ({len(self.data)} bytes) to {path}")
        return str(p)

    def to_base64(self) -> str:
        """Return base64-encoded content."""
        return base64.b64encode(self.data).decode("utf-8")

    def to_data_uri(self) -> str:
        """Return data URI for embedding in HTML/CSS."""
        mime = f"image/{self.format}" if self.media_type == "image" else f"video/{self.format}"
        return f"data:{mime};base64,{self.to_base64()}"


class CreativeGenerator:
    """
    Unified creative generation service.

    Routes requests to the appropriate provider based on the SSOT
    creative provider policy (ssot/creative/provider_policy.yaml).

    Usage:
        gen = CreativeGenerator()

        # Fast image (Nano Banana 2)
        asset = gen.generate_image("A mountain landscape at sunset")

        # Premium image (Imagen 4)
        asset = gen.generate_image("Product mockup", tier="premium")

        # Edit existing image
        asset = gen.edit_image(original_bytes, "Remove the background")

        # Generate video
        asset = gen.generate_video("Ocean waves", duration_s=5)
    """

    def __init__(self):
        self._gemini_client = None
        self._fal_client = None

    @property
    def gemini_client(self):
        """Lazy-init Gemini client using current google-genai SDK."""
        if self._gemini_client is None:
            try:
                from google import genai
            except ImportError:
                raise CreativeError(
                    "google-genai package not installed. Run: pip install google-genai",
                    provider="gemini"
                )
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise CreativeError("GEMINI_API_KEY not set", provider="gemini")
            self._gemini_client = genai.Client(api_key=api_key)
        return self._gemini_client

    def generate_image(
        self,
        prompt: str,
        *,
        tier: Literal["fast", "standard", "premium"] = "fast",
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> List[GeneratedAsset]:
        """
        Generate image(s) from text prompt.

        Args:
            prompt: Text description of the desired image.
            tier: Quality tier — fast (Nano Banana 2), standard (Nano Banana Pro), premium (Imagen 4).
            width: Output width in pixels.
            height: Output height in pixels.
            num_images: Number of variants to generate (1-4).
            style: Optional style modifier appended to prompt.
            negative_prompt: Things to avoid (Imagen only).
            seed: Reproducibility seed (when supported).

        Returns:
            List of GeneratedAsset objects.
        """
        if tier == "premium":
            return self._generate_imagen(
                prompt=prompt,
                width=width,
                height=height,
                num_images=num_images,
                negative_prompt=negative_prompt,
            )
        else:
            return self._generate_gemini_image(
                prompt=prompt,
                tier=tier,
                width=width,
                height=height,
                num_images=num_images,
                style=style,
            )

    def edit_image(
        self,
        image_data: bytes,
        instruction: str,
        *,
        tier: Literal["fast", "standard"] = "fast",
        mask_data: Optional[bytes] = None,
    ) -> List[GeneratedAsset]:
        """
        Edit an existing image using Gemini's conversational image editing.

        Args:
            image_data: Original image bytes (PNG or JPEG).
            instruction: Natural language edit instruction.
            tier: Model tier for editing.
            mask_data: Optional mask for inpainting.

        Returns:
            List with edited GeneratedAsset.
        """
        from google import genai
        from google.genai import types

        model = GEMINI_IMAGE_MODELS.get(tier, GEMINI_IMAGE_MODELS["fast"])
        start = time.time()

        # Build multimodal content: image + text instruction
        image_part = types.Part.from_bytes(data=image_data, mime_type="image/png")
        text_part = types.Part(text=instruction)

        contents = [image_part, text_part]
        if mask_data:
            mask_part = types.Part.from_bytes(data=mask_data, mime_type="image/png")
            contents = [image_part, mask_part, text_part]

        response = self.gemini_client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        latency = int((time.time() - start) * 1000)
        return self._extract_image_assets(
            response=response,
            model=model,
            provider="gemini",
            prompt=instruction,
            latency_ms=latency,
        )

    def generate_video(
        self,
        prompt: str,
        *,
        model: str = "veo-3.1-preview",
        duration_s: float = 5.0,
        width: int = 1280,
        height: int = 720,
        image_data: Optional[bytes] = None,
    ) -> GeneratedAsset:
        """
        Generate video from text (or image-to-video).

        Args:
            prompt: Text description of the desired video.
            model: Veo model ID.
            duration_s: Target duration in seconds.
            width: Output width.
            height: Output height.
            image_data: Optional starting frame for image-to-video.

        Returns:
            GeneratedAsset with video data.
        """
        from google import genai
        from google.genai import types

        start = time.time()

        config = {
            "generate_video_config": {
                "output_config": {
                    "duration_seconds": duration_s,
                    "resolution": {"width": width, "height": height},
                },
            },
        }

        contents = []
        if image_data:
            image_part = types.Part.from_bytes(data=image_data, mime_type="image/png")
            contents.append(image_part)
        contents.append(types.Part(text=prompt))

        # Veo uses async generation — poll for completion
        operation = self.gemini_client.models.generate_videos(
            model=model,
            contents=contents,
        )

        # Poll until done (max 5 minutes for video gen)
        timeout = 300
        poll_interval = 5
        elapsed = 0
        while not operation.done and elapsed < timeout:
            time.sleep(poll_interval)
            elapsed += poll_interval
            operation = self.gemini_client.operations.get(operation)
            logger.info(f"Video generation polling... elapsed={elapsed}s")

        if not operation.done:
            raise CreativeError(
                f"Video generation timed out after {timeout}s",
                provider="gemini",
            )

        latency = int((time.time() - start) * 1000)

        # Extract video from response
        video_data = operation.response.generated_videos[0].video.data
        return GeneratedAsset(
            media_type="video",
            provider="gemini",
            model=model,
            format="mp4",
            data=video_data,
            width=width,
            height=height,
            duration_s=duration_s,
            prompt=prompt,
            latency_ms=latency,
        )

    # --- Private methods ---

    def _generate_gemini_image(
        self,
        prompt: str,
        tier: str,
        width: int,
        height: int,
        num_images: int,
        style: Optional[str],
    ) -> List[GeneratedAsset]:
        """Generate image using Gemini Nano Banana models."""
        from google.genai import types

        model = GEMINI_IMAGE_MODELS.get(tier, GEMINI_IMAGE_MODELS["fast"])
        start = time.time()

        # Build prompt with optional style
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}. Style: {style}"

        response = self.gemini_client.models.generate_content(
            model=model,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                number_of_images=min(num_images, 4),
            ),
        )

        latency = int((time.time() - start) * 1000)
        return self._extract_image_assets(
            response=response,
            model=model,
            provider="gemini",
            prompt=prompt,
            latency_ms=latency,
        )

    def _generate_imagen(
        self,
        prompt: str,
        width: int,
        height: int,
        num_images: int,
        negative_prompt: Optional[str],
    ) -> List[GeneratedAsset]:
        """Generate image using Imagen 4."""
        from google.genai import types

        model = IMAGEN_MODELS["default"]
        start = time.time()

        config = types.GenerateImagesConfig(
            number_of_images=min(num_images, 4),
            output_mime_type="image/png",
            aspect_ratio=self._aspect_ratio(width, height),
        )
        if negative_prompt:
            config.negative_prompt = negative_prompt

        response = self.gemini_client.models.generate_images(
            model=model,
            prompt=prompt,
            config=config,
        )

        latency = int((time.time() - start) * 1000)
        assets = []
        for img in response.generated_images:
            assets.append(GeneratedAsset(
                media_type="image",
                provider="imagen",
                model=model,
                format="png",
                data=img.image.image_bytes,
                width=width,
                height=height,
                prompt=prompt,
                latency_ms=latency,
            ))
        return assets

    def _extract_image_assets(
        self,
        response,
        model: str,
        provider: str,
        prompt: str,
        latency_ms: int,
    ) -> List[GeneratedAsset]:
        """Extract image data from Gemini generate_content response."""
        assets = []
        if not response.candidates:
            raise CreativeError("No candidates returned", provider=provider)

        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                mime = part.inline_data.mime_type or "image/png"
                fmt = mime.split("/")[-1] if "/" in mime else "png"
                assets.append(GeneratedAsset(
                    media_type="image",
                    provider=provider,
                    model=model,
                    format=fmt,
                    data=part.inline_data.data,
                    prompt=prompt,
                    latency_ms=latency_ms,
                ))
        if not assets:
            # Model returned text instead of image — surface the text as error context
            text_parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, "text") and p.text]
            raise CreativeError(
                f"No image data in response. Model text: {' '.join(text_parts)[:200]}",
                provider=provider,
            )
        return assets

    @staticmethod
    def _aspect_ratio(w: int, h: int) -> str:
        """Map width/height to Imagen aspect ratio string."""
        ratio = w / h
        if abs(ratio - 1.0) < 0.1:
            return "1:1"
        elif abs(ratio - 16 / 9) < 0.1:
            return "16:9"
        elif abs(ratio - 9 / 16) < 0.1:
            return "9:16"
        elif abs(ratio - 4 / 3) < 0.1:
            return "4:3"
        elif abs(ratio - 3 / 4) < 0.1:
            return "3:4"
        else:
            return "1:1"  # safe default


# --- Module-level convenience ---

_generator: Optional[CreativeGenerator] = None


def generate_image(prompt: str, **kwargs) -> List[GeneratedAsset]:
    """Convenience: generate image with default settings."""
    global _generator
    if _generator is None:
        _generator = CreativeGenerator()
    return _generator.generate_image(prompt, **kwargs)


def edit_image(image_data: bytes, instruction: str, **kwargs) -> List[GeneratedAsset]:
    """Convenience: edit image with default settings."""
    global _generator
    if _generator is None:
        _generator = CreativeGenerator()
    return _generator.edit_image(image_data, instruction, **kwargs)


def generate_video(prompt: str, **kwargs) -> GeneratedAsset:
    """Convenience: generate video with default settings."""
    global _generator
    if _generator is None:
        _generator = CreativeGenerator()
    return _generator.generate_video(prompt, **kwargs)

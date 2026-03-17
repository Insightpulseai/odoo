import { CaptureResult } from "@ipai/browser-agent-contract";

const UPLOAD_ENDPOINT = "http://localhost:8766/api/captures";

export async function uploadAndAttach(
  capture: CaptureResult,
  sessionId?: string
): Promise<{ ok: boolean; captureId: string; uploadedUrl?: string }> {
  // For data URLs (tab captures), convert to blob
  let body: FormData | string;
  const formData = new FormData();

  if (capture.image_ref.startsWith("data:")) {
    const response = await fetch(capture.image_ref);
    const blob = await response.blob();
    formData.append("image", blob, `${capture.capture_id}.png`);
  } else {
    // For file paths (native captures), send the path for server-side read
    formData.append("file_path", capture.image_ref);
  }

  formData.append("capture_id", capture.capture_id);
  formData.append("capture_type", capture.capture_type);
  formData.append("captured_at", capture.captured_at);
  formData.append("metadata", JSON.stringify(capture.source));
  if (sessionId) formData.append("session_id", sessionId);

  try {
    const resp = await fetch(UPLOAD_ENDPOINT, {
      method: "POST",
      body: formData,
    });

    if (!resp.ok) {
      throw new Error(`Upload failed: ${resp.status} ${resp.statusText}`);
    }

    const result = await resp.json();
    return { ok: true, captureId: capture.capture_id, uploadedUrl: result.url };
  } catch (err) {
    console.error("[upload] Failed:", err);
    // Store locally as fallback
    await chrome.storage.local.set({
      [`pending_${capture.capture_id}`]: capture,
    });
    return { ok: false, captureId: capture.capture_id };
  }
}

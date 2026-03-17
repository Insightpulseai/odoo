import { CaptureResult, NativeHostResponse, generateCaptureId } from "@ipai/browser-agent-contract";

const NATIVE_HOST = "com.insightpulseai.screen";

export async function captureActiveWindow(): Promise<CaptureResult> {
  const captureId = generateCaptureId();

  const response: NativeHostResponse = await chrome.runtime.sendNativeMessage(
    NATIVE_HOST,
    { action: "capture_active_window" }
  );

  if (response.error) {
    throw new Error(`Native capture failed: ${response.error}`);
  }

  return {
    capture_id: response.capture_id || captureId,
    capture_type: "active_window",
    image_ref: response.file_path,
    mime_type: response.mime_type as "image/png",
    width: response.width,
    height: response.height,
    captured_at: new Date().toISOString(),
    source: {
      browser: "chrome",
    },
  };
}

export async function captureFullScreen(): Promise<CaptureResult> {
  const captureId = generateCaptureId();

  const response: NativeHostResponse = await chrome.runtime.sendNativeMessage(
    NATIVE_HOST,
    { action: "capture_full_screen" }
  );

  if (response.error) {
    throw new Error(`Native capture failed: ${response.error}`);
  }

  return {
    capture_id: response.capture_id || captureId,
    capture_type: "full_screen",
    image_ref: response.file_path,
    mime_type: response.mime_type as "image/png",
    width: response.width,
    height: response.height,
    captured_at: new Date().toISOString(),
    source: {
      browser: "chrome",
    },
  };
}

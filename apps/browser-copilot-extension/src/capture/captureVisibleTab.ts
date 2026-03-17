import { CaptureResult, generateCaptureId } from "@ipai/browser-agent-contract";

export async function captureVisibleTab(): Promise<CaptureResult> {
  const captureId = generateCaptureId();

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) throw new Error("No active tab found");

  const dataUrl = await chrome.tabs.captureVisibleTab(undefined, {
    format: "png",
    quality: 100,
  });

  return {
    capture_id: captureId,
    capture_type: "current_tab",
    image_ref: dataUrl,
    mime_type: "image/png",
    width: tab.width ?? 0,
    height: tab.height ?? 0,
    captured_at: new Date().toISOString(),
    source: {
      browser: "chrome",
      tab_id: tab.id,
      tab_url: tab.url,
      tab_title: tab.title,
      window_id: tab.windowId,
    },
  };
}

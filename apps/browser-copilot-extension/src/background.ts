import { normalizeCommand, AgentIntent } from "@ipai/browser-agent-contract";
import { captureVisibleTab } from "./capture/captureVisibleTab.js";
import { captureActiveWindow, captureFullScreen } from "./capture/captureActiveWindow.js";
import { uploadAndAttach } from "./api/uploadAndAttach.js";

// Handle keyboard shortcut
chrome.commands.onCommand.addListener(async (command) => {
  if (command === "capture-active-window") {
    await executeCaptureIntent("capture.active_window");
  }
});

// Handle messages from side panel
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "agent.command" && typeof msg?.text === "string") {
    const intent = normalizeCommand(msg.text);
    if (intent) {
      executeCaptureIntent(intent)
        .then((result) => sendResponse({ type: "capture.complete", ...result }))
        .catch((err) => sendResponse({ type: "capture.error", error: String(err) }));
      return true; // async response
    }
    sendResponse({ type: "capture.error", error: `Unknown command: ${msg.text}` });
  }
  return false;
});

// Open side panel on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
});

async function executeCaptureIntent(intent: AgentIntent) {
  let capture;

  switch (intent) {
    case "capture.current_tab":
    case "capture.and_analyze":
    case "capture.summarize_page":
      capture = await captureVisibleTab();
      break;
    case "capture.active_window":
      try {
        capture = await captureActiveWindow();
      } catch {
        // Fallback to tab capture if native host unavailable
        console.warn("[bg] Native host unavailable, falling back to tab capture");
        capture = await captureVisibleTab();
      }
      break;
    case "capture.full_screen":
      capture = await captureFullScreen();
      break;
    default:
      throw new Error(`Unhandled intent: ${intent}`);
  }

  // Upload and attach to session
  const result = await uploadAndAttach(capture);

  // Notify side panel
  chrome.runtime.sendMessage({
    type: "capture.complete",
    captureId: capture.capture_id,
    imageRef: capture.image_ref,
    captureType: capture.capture_type,
  }).catch(() => {/* side panel may not be open */});

  return { captureId: capture.capture_id, captureType: capture.capture_type, ok: result.ok };
}

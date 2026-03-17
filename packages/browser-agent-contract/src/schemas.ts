export interface SidePanelCommand {
  type: "agent.command";
  text: string;
  timestamp: string;
}

export interface CaptureComplete {
  type: "capture.complete";
  captureId: string;
  imageRef: string;
  captureType: string;
}

export interface CaptureError {
  type: "capture.error";
  error: string;
}

export type ExtensionMessage = SidePanelCommand | CaptureComplete | CaptureError;

export interface CaptureRequest {
  action: "capture_active_window" | "capture_full_screen" | "capture_current_tab";
}

export interface CaptureResult {
  capture_id: string;
  capture_type: "current_tab" | "active_window" | "full_screen";
  image_ref: string;
  mime_type: "image/png" | "image/jpeg";
  width: number;
  height: number;
  captured_at: string;
  source: {
    browser?: string;
    tab_id?: number;
    tab_url?: string;
    tab_title?: string;
    window_id?: number;
  };
}

export interface NativeHostRequest {
  action: "capture_active_window" | "capture_full_screen";
}

export interface NativeHostResponse {
  capture_id: string;
  file_path: string;
  mime_type: string;
  width: number;
  height: number;
  source: "active_window" | "full_screen";
  error?: string;
}

export function generateCaptureId(): string {
  const now = new Date();
  const ts = now.toISOString().replace(/[-:T]/g, "").slice(0, 15);
  return `cap_${ts}`;
}

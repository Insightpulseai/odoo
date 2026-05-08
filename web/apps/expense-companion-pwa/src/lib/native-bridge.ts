/**
 * Type-safe wrapper around `window.__nativeBridge` — the JS shim injected by
 * the iOS WKWebView wrapper at `web/mobile/Sources/JSBridge.swift`.
 *
 * In a browser, every method returns `null` and `isNative` is `false`, so
 * callers can use the same code path on web and inside the iOS shell.
 *
 * Concur parity: the iOS bridge gives us native camera, on-device queue,
 * Face ID, mileage, keychain, and haptics — all the things a pure browser
 * PWA can't reach.
 */

export interface NativeReceiptData {
  merchant_name: string | null;
  total: number | null;
  subtotal: number | null;
  tax: number | null;
  tip: number | null;
  currency: string | null;
  transaction_date: string | null;
  transaction_time: string | null;
  doc_type: string | null;
  confidence: number | null;
  items: Array<{
    name: string | null;
    quantity: number | null;
    price: number | null;
    total: number | null;
  }> | null;
}

interface NativeBridge {
  isNative: boolean;
  biometricAuth: () => Promise<{ authenticated: boolean }>;
  captureReceipt: () => Promise<{ imageBase64: string }>;
  ocrAnalyze: (imageBase64: string) => Promise<NativeReceiptData>;
  queueReceipt: (imageBase64: string) => Promise<{ entryId: string }>;
  queuePending: () => Promise<{ pending: string[] }>;
  mileageStart: () => Promise<{ tracking: boolean }>;
  mileageStop: () => Promise<{
    distanceMeters: number;
    distanceKilometers: number;
  }>;
  mileageStatus: () => Promise<{
    distanceMeters: number;
    distanceKilometers: number;
  }>;
  keychainSet: (key: string, value: string) => Promise<{ ok: boolean }>;
  keychainGet: (key: string) => Promise<{ value: string | null }>;
  haptic: (
    style?: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft',
  ) => Promise<{ ok: boolean }>;
}

declare global {
  interface Window {
    __nativeBridge?: NativeBridge;
  }
}

/** Whether the PWA is running inside the iOS native wrapper. */
export function isNative(): boolean {
  return typeof window !== 'undefined' && window.__nativeBridge?.isNative === true;
}

/** Returns the native bridge if available, else `null`. */
export function nativeBridge(): NativeBridge | null {
  if (typeof window === 'undefined') return null;
  return window.__nativeBridge ?? null;
}

/** Convert a base64 string to a `File` object (for FormData uploads). */
export function base64ToFile(
  base64: string,
  filename = 'receipt.jpg',
  mimeType = 'image/jpeg',
): File {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new File([bytes], filename, { type: mimeType });
}

/**
 * Trigger native haptic feedback if available; no-op in browser.
 * Use sparingly — major successful actions only.
 */
export function haptic(style: 'light' | 'medium' | 'heavy' = 'medium'): void {
  const bridge = nativeBridge();
  if (bridge) void bridge.haptic(style);
}

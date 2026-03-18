import { loggers } from '@/shared/logger';

const logger = loggers.vision;

/**
 * Offscreen Document Entry Point
 * Isolated context for heavy compute (ONNX inference, WebGPU)
 * Used for vision processing without blocking main extension contexts
 */

logger.info('Offscreen document loaded');

/**
 * Message handler for vision processing requests
 */
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  logger.debug('Message received:', message.type);

  switch (message.type) {
    case 'process-screenshot':
      processScreenshot(message.payload)
        .then(result => sendResponse({ ok: true, result }))
        .catch(error => sendResponse({ ok: false, error: error.message }));
      return true; // Keep channel open

    case 'run-ocr':
      runOCR(message.payload)
        .then(result => sendResponse({ ok: true, result }))
        .catch(error => sendResponse({ ok: false, error: error.message }));
      return true;

    case 'verify-visual':
      verifyVisual(message.payload)
        .then(result => sendResponse({ ok: true, result }))
        .catch(error => sendResponse({ ok: false, error: error.message }));
      return true;

    default:
      logger.warn('Unknown message type:', message.type);
      sendResponse({ ok: false, error: 'Unknown message type' });
  }
});

/**
 * Process screenshot for visual grounding
 * Phase 2: Will use ONNX Runtime Web for DeepSeek-OCR inference
 */
async function processScreenshot(_payload: { dataUrl: string }): Promise<unknown> {
  logger.info('Processing screenshot for visual grounding');

  // TODO: Phase 2 - Implement ONNX inference
  // 1. Load DeepSeek-OCR model (INT8 quantized)
  // 2. Run inference on screenshot
  // 3. Extract text + bounding boxes
  // 4. Generate visual signatures (SHA-256 hashes)

  return {
    message: 'Phase 2: Vision processing not yet implemented',
    timestamp: Date.now()
  };
}

/**
 * Run OCR on screenshot
 * Phase 2: Will extract text and bounding boxes
 */
async function runOCR(_payload: { dataUrl: string }): Promise<unknown> {
  logger.info('Running OCR on screenshot');

  // TODO: Phase 2 - Implement OCR
  // Use DeepSeek-OCR or fallback to cloud API (Google Vision)

  return {
    text: [],
    timestamp: Date.now()
  };
}

/**
 * Verify visual changes (before/after comparison)
 * Phase 2: Will use pixelmatch + SSIM
 */
async function verifyVisual(_payload: { before: string; after: string }): Promise<unknown> {
  logger.info('Verifying visual changes');

  // TODO: Phase 2 - Implement visual verification
  // 1. Decode WebP images
  // 2. Run pixelmatch for pixel-level diff
  // 3. Calculate SSIM for structural similarity
  // 4. Return confidence score

  return {
    success: false,
    confidence: 0,
    message: 'Phase 2: Visual verification not yet implemented'
  };
}

logger.info('Offscreen document ready');

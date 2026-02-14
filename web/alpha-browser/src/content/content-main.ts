import { loggers } from '@/shared/logger';
import type { AgentMessage, DOMAction } from '@/shared/types';

const logger = loggers.content;

/**
 * Content Script Entry Point
 * Injects into all pages, handles DOM manipulation and screenshot capture
 */

logger.info('Content script injected');

/**
 * Message handler from service worker
 */
chrome.runtime.onMessage.addListener(
  (message: AgentMessage, _sender, sendResponse) => {
    logger.debug('Message received from service worker:', message);

    switch (message.type) {
      case 'task-assignment':
        handleTaskAssignment(message.payload as { action: DOMAction })
          .then(result => sendResponse({ ok: true, result }))
          .catch(error => sendResponse({ ok: false, error: error.message }));
        return true; // Keep channel open for async response

      default:
        logger.warn('Unknown message type:', message.type);
        sendResponse({ ok: false, error: 'Unknown message type' });
    }
  }
);

/**
 * Handle task assignment from Governor
 */
async function handleTaskAssignment(payload: { action: DOMAction }): Promise<unknown> {
  const { action } = payload;
  logger.info('Executing action:', action.type);

  try {
    switch (action.type) {
      case 'click':
        return await executeClick(action);
      case 'type':
        return await executeType(action);
      case 'scroll':
        return await executeScroll(action);
      case 'hover':
        return await executeHover(action);
      case 'navigate':
        return await executeNavigate(action);
      case 'extract':
        return await executeExtract(action);
      default:
        throw new Error(`Unknown action type: ${action.type}`);
    }
  } catch (error) {
    logger.error('Action failed:', error);
    throw error;
  }
}

/**
 * Execute click action
 */
async function executeClick(action: DOMAction): Promise<{ success: boolean }> {
  const element = await findElement(action.target.domSelector);
  if (!element) {
    throw new Error('Element not found');
  }

  // Simulate human-like click
  element.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
  await sleep(50);
  element.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
  element.dispatchEvent(new MouseEvent('click', { bubbles: true }));

  logger.debug('Click executed successfully');
  return { success: true };
}

/**
 * Execute type action
 */
async function executeType(action: DOMAction): Promise<{ success: boolean }> {
  const element = await findElement(action.target.domSelector);
  if (!element || !(element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement)) {
    throw new Error('Input element not found');
  }

  const text = action.payload?.text || '';

  // Clear existing value
  element.value = '';
  element.dispatchEvent(new Event('input', { bubbles: true }));

  // Type character by character (simulate human typing)
  for (const char of text) {
    element.value += char;
    element.dispatchEvent(new Event('input', { bubbles: true }));
    await sleep(50); // 50ms between characters
  }

  element.dispatchEvent(new Event('change', { bubbles: true }));
  logger.debug('Type executed successfully');
  return { success: true };
}

/**
 * Execute scroll action
 */
async function executeScroll(action: DOMAction): Promise<{ success: boolean }> {
  const x = action.payload?.x || 0;
  const y = action.payload?.y || 0;

  window.scrollTo({
    left: x,
    top: y,
    behavior: 'smooth'
  });

  await sleep(300); // Wait for scroll to complete
  logger.debug('Scroll executed successfully');
  return { success: true };
}

/**
 * Execute hover action
 */
async function executeHover(action: DOMAction): Promise<{ success: boolean }> {
  const element = await findElement(action.target.domSelector);
  if (!element) {
    throw new Error('Element not found');
  }

  element.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
  element.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));

  logger.debug('Hover executed successfully');
  return { success: true };
}

/**
 * Execute navigate action
 */
async function executeNavigate(action: DOMAction): Promise<{ success: boolean }> {
  const url = action.payload?.url;
  if (!url) {
    throw new Error('URL not provided');
  }

  window.location.href = url;
  logger.debug('Navigate executed successfully');
  return { success: true };
}

/**
 * Execute extract action (data extraction)
 */
async function executeExtract(action: DOMAction): Promise<{ data: unknown }> {
  const element = await findElement(action.target.domSelector);
  if (!element) {
    throw new Error('Element not found');
  }

  // Extract text content and attributes
  const data = {
    text: element.textContent?.trim(),
    html: element.innerHTML,
    attributes: Array.from(element.attributes).reduce((acc, attr) => {
      acc[attr.name] = attr.value;
      return acc;
    }, {} as Record<string, string>)
  };

  logger.debug('Extract executed successfully');
  return { data };
}

/**
 * Find element by selector (with retry)
 */
async function findElement(selector?: string): Promise<Element | null> {
  if (!selector) {
    throw new Error('Selector not provided');
  }

  // Try up to 3 times with 500ms delay
  for (let i = 0; i < 3; i++) {
    const element = document.querySelector(selector);
    if (element) return element;
    await sleep(500);
  }

  return null;
}

/**
 * Sleep utility
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Capture screenshot (via service worker)
 */
export async function captureScreenshot(): Promise<string> {
  // Request screenshot from service worker
  const response = await chrome.runtime.sendMessage({
    type: 'capture-screenshot'
  });

  return response.dataUrl;
}

/**
 * Extract DOM structure for vision processing
 */
export function extractDOM(): unknown {
  // TODO: Implement DOM-to-JSON serialization
  return {
    url: window.location.href,
    title: document.title,
    elements: [] // Extract visible elements with bounding boxes
  };
}

logger.info('Content script ready');

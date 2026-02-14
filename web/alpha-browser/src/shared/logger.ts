import type { Logger } from './types';

/**
 * Structured logger for Alpha Browser
 * Logs include timestamp, level, and context
 */
class AlphaLogger implements Logger {
  private context: string;

  constructor(context: string) {
    this.context = context;
  }

  private log(level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR', message: string, ...args: unknown[]): void {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level}] [${this.context}]`;

    switch (level) {
      case 'DEBUG':
        console.debug(prefix, message, ...args);
        break;
      case 'INFO':
        console.info(prefix, message, ...args);
        break;
      case 'WARN':
        console.warn(prefix, message, ...args);
        break;
      case 'ERROR':
        console.error(prefix, message, ...args);
        break;
    }
  }

  debug(message: string, ...args: unknown[]): void {
    this.log('DEBUG', message, ...args);
  }

  info(message: string, ...args: unknown[]): void {
    this.log('INFO', message, ...args);
  }

  warn(message: string, ...args: unknown[]): void {
    this.log('WARN', message, ...args);
  }

  error(message: string, ...args: unknown[]): void {
    this.log('ERROR', message, ...args);
  }
}

/**
 * Create a logger instance for a specific context
 */
export function createLogger(context: string): Logger {
  return new AlphaLogger(context);
}

/**
 * Global logger instances
 */
export const loggers = {
  serviceWorker: createLogger('ServiceWorker'),
  governor: createLogger('Governor'),
  domWorker: createLogger('DOMWorker'),
  formWorker: createLogger('FormWorker'),
  navWorker: createLogger('NavWorker'),
  extractWorker: createLogger('ExtractWorker'),
  verifyWorker: createLogger('VerifyWorker'),
  content: createLogger('ContentScript'),
  popup: createLogger('Popup'),
  storage: createLogger('Storage'),
  vision: createLogger('Vision'),
  llm: createLogger('LLM'),
  identity: createLogger('Identity')
};

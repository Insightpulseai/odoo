type Severity = 'error' | 'warn' | 'info';

type DiagnosticSource =
  | 'console'
  | 'window.onerror'
  | 'unhandledrejection'
  | 'react-error-boundary';

export interface DiagnosticEntry {
  id: string;
  severity: Severity;
  message: string;
  timestamp: number;
  source: DiagnosticSource;
  route?: string;
  stack?: string;
}

type Subscriber = () => void;

export interface ConsoleBridge {
  entries: () => DiagnosticEntry[];
  clear: () => void;
  destroy: () => void;
  subscribe: (callback: Subscriber) => () => void;
  report: (
    severity: Severity,
    message: string,
    source: DiagnosticSource,
    stack?: string,
  ) => void;
}

interface ConsoleBridgeOptions {
  maxEntries?: number;
}

const MAX_ENTRIES_DEFAULT = 200;

let idCounter = 0;

function nextId(): string {
  idCounter += 1;
  return `diag-${idCounter}-${Date.now()}`;
}

function currentRoute(): string | undefined {
  if (typeof window !== 'undefined') {
    return window.location.pathname + window.location.search;
  }
  return undefined;
}

const NO_OP_BRIDGE: ConsoleBridge = {
  entries: () => [],
  clear: () => {},
  destroy: () => {},
  subscribe: () => () => {},
  report: () => {},
};

export function createConsoleBridge(
  opts?: ConsoleBridgeOptions,
): ConsoleBridge {
  if (process.env.NODE_ENV === 'production') {
    return NO_OP_BRIDGE;
  }

  const maxEntries = opts?.maxEntries ?? MAX_ENTRIES_DEFAULT;
  let buffer: DiagnosticEntry[] = [];
  const subscribers = new Set<Subscriber>();
  let destroyed = false;

  function notify(): void {
    for (const cb of subscribers) {
      cb();
    }
  }

  function push(entry: DiagnosticEntry): void {
    if (destroyed) return;
    buffer.push(entry);
    if (buffer.length > maxEntries) {
      buffer = buffer.slice(buffer.length - maxEntries);
    }
    notify();
  }

  function report(
    severity: Severity,
    message: string,
    source: DiagnosticSource,
    stack?: string,
  ): void {
    push({
      id: nextId(),
      severity,
      message,
      timestamp: Date.now(),
      source,
      route: currentRoute(),
      stack,
    });
  }

  // --- Console interception ---

  const originalConsoleError = console.error;
  const originalConsoleWarn = console.warn;

  console.error = new Proxy(originalConsoleError, {
    apply(target, thisArg, args: unknown[]) {
      const message = args
        .map((a) => (typeof a === 'string' ? a : String(a)))
        .join(' ');
      const stack =
        args[0] instanceof Error ? args[0].stack : new Error().stack;
      report('error', message, 'console', stack);
      return Reflect.apply(target, thisArg, args);
    },
  });

  console.warn = new Proxy(originalConsoleWarn, {
    apply(target, thisArg, args: unknown[]) {
      const message = args
        .map((a) => (typeof a === 'string' ? a : String(a)))
        .join(' ');
      report('warn', message, 'console');
      return Reflect.apply(target, thisArg, args);
    },
  });

  // --- Global error listeners ---

  function handleError(event: ErrorEvent): void {
    report(
      'error',
      event.message || 'Unknown error',
      'window.onerror',
      event.error?.stack,
    );
  }

  function handleRejection(event: PromiseRejectionEvent): void {
    const reason = event.reason;
    const message =
      reason instanceof Error
        ? reason.message
        : typeof reason === 'string'
          ? reason
          : 'Unhandled promise rejection';
    const stack = reason instanceof Error ? reason.stack : undefined;
    report('error', message, 'unhandledrejection', stack);
  }

  if (typeof window !== 'undefined') {
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleRejection);
  }

  // --- Public API ---

  const bridge: ConsoleBridge = {
    entries: () => buffer,

    clear: () => {
      buffer = [];
      notify();
    },

    destroy: () => {
      destroyed = true;
      console.error = originalConsoleError;
      console.warn = originalConsoleWarn;
      if (typeof window !== 'undefined') {
        window.removeEventListener('error', handleError);
        window.removeEventListener('unhandledrejection', handleRejection);
      }
      subscribers.clear();
      buffer = [];
    },

    subscribe: (callback: Subscriber) => {
      subscribers.add(callback);
      return () => {
        subscribers.delete(callback);
      };
    },

    report,
  };

  return bridge;
}

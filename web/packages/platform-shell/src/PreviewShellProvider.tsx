import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  useSyncExternalStore,
} from 'react';
import type { ReactNode } from 'react';
import { FluentProvider, webDarkTheme, webLightTheme } from '@fluentui/react-components';
import { createConsoleBridge } from './console-bridge';
import type { ConsoleBridge, DiagnosticEntry } from './console-bridge';

interface PreviewShellContextValue {
  entries: DiagnosticEntry[];
  diagnosticsOpen: boolean;
  toggleDiagnostics: () => void;
  clearDiagnostics: () => void;
  reportError: (error: Error, source?: string) => void;
}

const NO_OP_CONTEXT: PreviewShellContextValue = {
  entries: [],
  diagnosticsOpen: false,
  toggleDiagnostics: () => {},
  clearDiagnostics: () => {},
  reportError: () => {},
};

const PreviewShellContext =
  createContext<PreviewShellContextValue>(NO_OP_CONTEXT);

interface PreviewShellProviderProps {
  children: ReactNode;
  defaultDiagnosticsOpen?: boolean;
  theme?: 'light' | 'dark';
}

function ActiveProvider({
  children,
  defaultDiagnosticsOpen = false,
  theme = 'dark',
}: PreviewShellProviderProps) {
  const bridgeRef = useRef<ConsoleBridge | null>(null);

  if (bridgeRef.current === null) {
    bridgeRef.current = createConsoleBridge();
  }

  const bridge = bridgeRef.current;

  const entries = useSyncExternalStore(
    bridge.subscribe,
    bridge.entries,
    () => [] as DiagnosticEntry[],
  );

  const [diagnosticsOpen, setDiagnosticsOpen] = useState(
    defaultDiagnosticsOpen,
  );

  const toggleDiagnostics = useCallback(() => {
    setDiagnosticsOpen((prev) => !prev);
  }, []);

  const clearDiagnostics = useCallback(() => {
    bridge.clear();
  }, [bridge]);

  const reportError = useCallback(
    (error: Error, source?: string) => {
      bridge.report(
        'error',
        error.message,
        (source as DiagnosticEntry['source']) ?? 'react-error-boundary',
        error.stack,
      );
    },
    [bridge],
  );

  useEffect(() => {
    return () => {
      bridgeRef.current?.destroy();
    };
  }, []);

  const value: PreviewShellContextValue = {
    entries,
    diagnosticsOpen,
    toggleDiagnostics,
    clearDiagnostics,
    reportError,
  };

  const fluentTheme = theme === 'dark' ? webDarkTheme : webLightTheme;

  return (
    <FluentProvider theme={fluentTheme}>
      <PreviewShellContext.Provider value={value}>
        {children}
      </PreviewShellContext.Provider>
    </FluentProvider>
  );
}

export function PreviewShellProvider(props: PreviewShellProviderProps) {
  if (process.env.NODE_ENV === 'production') {
    return (
      <PreviewShellContext.Provider value={NO_OP_CONTEXT}>
        {props.children}
      </PreviewShellContext.Provider>
    );
  }

  return <ActiveProvider {...props} />;
}

export function usePreviewShell(): PreviewShellContextValue {
  return useContext(PreviewShellContext);
}

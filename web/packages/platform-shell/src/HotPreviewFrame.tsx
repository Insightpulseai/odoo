import React, { Component, useCallback, useRef, useState } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { makeStyles, tokens, Button, Text, Spinner } from '@fluentui/react-components';
import { ErrorCircleRegular } from '@fluentui/react-icons';

// --- ErrorBoundary (internal) ---

interface ErrorBoundaryProps {
  children: ReactNode;
  onError?: (error: Error) => void;
  fallback: (error: Error, reset: () => void) => ReactNode;
}

interface ErrorBoundaryState {
  error: Error | null;
}

class PreviewErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    this.props.onError?.(error);
    if (process.env.NODE_ENV !== 'production') {
      console.debug('[platform-shell] ErrorBoundary caught:', error, info.componentStack);
    }
  }

  reset = (): void => {
    this.setState({ error: null });
  };

  render(): ReactNode {
    if (this.state.error) {
      return this.props.fallback(this.state.error, this.reset);
    }
    return this.props.children;
  }
}

// --- Styles ---

const useStyles = makeStyles({
  frame: {
    position: 'relative',
    width: '100%',
    height: '100%',
  },
  reloadBar: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '2px',
    zIndex: 10,
    overflow: 'hidden',
    backgroundColor: tokens.colorBrandBackground,
    animationName: {
      '0%': { transform: 'translateX(-100%)' },
      '50%': { transform: 'translateX(0)' },
      '100%': { transform: 'translateX(100%)' },
    },
    animationDuration: '1.2s',
    animationTimingFunction: tokens.curveEasyEase,
    animationIterationCount: 'infinite',
  },
  loading: {
    position: 'absolute',
    inset: '0',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: tokens.colorNeutralBackground1,
    zIndex: 5,
  },
  iframe: {
    width: '100%',
    height: '100%',
    border: 'none',
  },
  errorFallback: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%',
    backgroundColor: tokens.colorNeutralBackground1,
    padding: tokens.spacingHorizontalXXL,
    textAlign: 'center',
  },
  errorIcon: {
    width: '48px',
    height: '48px',
    borderRadius: tokens.borderRadiusCircular,
    backgroundColor: tokens.colorPaletteRedBackground1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: tokens.spacingVerticalM,
    color: tokens.colorPaletteRedForeground1,
  },
  errorMessage: {
    fontFamily: tokens.fontFamilyMonospace,
    fontSize: tokens.fontSizeBase200,
    color: tokens.colorPaletteRedForeground1,
    marginBottom: tokens.spacingVerticalM,
    wordBreak: 'break-word',
  },
});

// --- Sub-components ---

function ReloadBar() {
  const styles = useStyles();
  return <div className={styles.reloadBar} />;
}

function IframePreview({ src, isReloading }: { src: string; isReloading?: boolean }) {
  const [loaded, setLoaded] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const styles = useStyles();

  const handleLoad = useCallback(() => {
    setLoaded(true);
  }, []);

  return (
    <div className={styles.frame}>
      {isReloading && <ReloadBar />}
      {!loaded && (
        <div className={styles.loading}>
          <Spinner size="small" label="Loading preview..." />
        </div>
      )}
      <iframe
        ref={iframeRef}
        src={src}
        onLoad={handleLoad}
        title="Preview"
        className={styles.iframe}
        sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
      />
    </div>
  );
}

function ErrorFallback({ error, onReset }: { error: Error; onReset: () => void }) {
  const styles = useStyles();
  return (
    <div className={styles.errorFallback}>
      <div className={styles.errorIcon}>
        <ErrorCircleRegular fontSize={24} />
      </div>
      <Text weight="semibold" size={400}>Preview crashed</Text>
      <Text className={styles.errorMessage}>{error.message}</Text>
      <Button appearance="secondary" onClick={onReset}>Retry</Button>
    </div>
  );
}

// --- Main component ---

interface HotPreviewFrameProps {
  src?: string;
  children?: ReactNode;
  isReloading?: boolean;
  onError?: (error: Error) => void;
  className?: string;
}

export function HotPreviewFrame({
  src,
  children,
  isReloading,
  onError,
  className,
}: HotPreviewFrameProps) {
  const styles = useStyles();

  if (src) {
    return (
      <div className={`${styles.frame} ${className ?? ''}`}>
        <IframePreview src={src} isReloading={isReloading} />
      </div>
    );
  }

  return (
    <div className={`${styles.frame} ${className ?? ''}`}>
      {isReloading && <ReloadBar />}
      <PreviewErrorBoundary
        onError={onError}
        fallback={(error, reset) => <ErrorFallback error={error} onReset={reset} />}
      >
        {children}
      </PreviewErrorBoundary>
    </div>
  );
}

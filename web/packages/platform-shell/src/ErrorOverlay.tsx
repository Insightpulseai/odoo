import React from 'react';

interface ErrorOverlayProps {
  error: Error | null;
  onDismiss: () => void;
}

/**
 * Full-screen fatal error overlay for development.
 * Uses INLINE styles exclusively for crash resilience --
 * if CSS fails to load, this overlay still renders correctly.
 * Returns null in production or when no error is present.
 */
export function ErrorOverlay({ error, onDismiss }: ErrorOverlayProps) {
  if (process.env.NODE_ENV === 'production') {
    return null;
  }

  if (!error) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 99999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        backdropFilter: 'blur(4px)',
        padding: '24px',
      }}
      role="alertdialog"
      aria-modal="true"
      aria-label="Fatal error"
    >
      <div
        style={{
          maxWidth: '720px',
          width: '100%',
          maxHeight: '80vh',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#18181b',
          border: '1px solid #ef4444',
          borderRadius: '12px',
          overflow: 'hidden',
          boxShadow: '0 0 60px rgba(239, 68, 68, 0.15)',
        }}
      >
        {/* Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '16px 20px',
            borderBottom: '1px solid #27272a',
            backgroundColor: '#1c1017',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span
              style={{
                display: 'inline-block',
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                backgroundColor: '#ef4444',
              }}
            />
            <span
              style={{
                color: '#fca5a5',
                fontSize: '14px',
                fontWeight: 600,
                fontFamily:
                  'ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace',
              }}
            >
              Uncaught Error
            </span>
          </div>
          <button
            type="button"
            onClick={onDismiss}
            style={{
              color: '#a1a1aa',
              fontSize: '13px',
              fontFamily:
                'ui-sans-serif, system-ui, -apple-system, sans-serif',
              backgroundColor: '#27272a',
              border: '1px solid #3f3f46',
              borderRadius: '6px',
              padding: '6px 14px',
              cursor: 'pointer',
              transition: 'background-color 0.15s',
            }}
            onMouseEnter={(e) => {
              (e.target as HTMLButtonElement).style.backgroundColor = '#3f3f46';
            }}
            onMouseLeave={(e) => {
              (e.target as HTMLButtonElement).style.backgroundColor = '#27272a';
            }}
          >
            Dismiss
          </button>
        </div>

        {/* Error message */}
        <div
          style={{
            padding: '20px',
            borderBottom: '1px solid #27272a',
          }}
        >
          <p
            style={{
              color: '#f87171',
              fontSize: '16px',
              fontWeight: 600,
              fontFamily:
                'ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace',
              margin: 0,
              lineHeight: 1.6,
              wordBreak: 'break-word',
            }}
          >
            {error.message}
          </p>
        </div>

        {/* Stack trace */}
        {error.stack && (
          <div
            style={{
              flex: 1,
              overflow: 'auto',
              padding: '16px 20px',
            }}
          >
            <pre
              style={{
                color: '#a1a1aa',
                fontSize: '12px',
                fontFamily:
                  'ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace',
                lineHeight: 1.7,
                margin: 0,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {error.stack}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

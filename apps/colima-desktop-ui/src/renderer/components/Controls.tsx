import React, { useState } from 'react';
import type { VMState } from '../../../../tools/colima-desktop/src/shared/contracts/status';

interface ControlButtonProps {
  label: string;
  onClick: () => Promise<void>;
  disabled: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
  loading?: boolean;
}

function ControlButton({ label, onClick, disabled, variant = 'secondary', loading }: ControlButtonProps) {
  const [isProcessing, setIsProcessing] = useState(false);

  const handleClick = async () => {
    setIsProcessing(true);
    try {
      await onClick();
    } catch (err) {
      console.error('Control action failed:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const isDisabled = disabled || isProcessing || loading;

  return (
    <button
      className={`control-button control-button--${variant}`}
      onClick={handleClick}
      disabled={isDisabled}
      aria-busy={isProcessing || loading}
    >
      {isProcessing || loading ? (
        <>
          <span className="control-spinner" aria-hidden="true" />
          <span>{label}...</span>
        </>
      ) : (
        label
      )}
    </button>
  );
}

export function Controls() {
  const [vmState, setVmState] = useState<VMState>('stopped');
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await window.colima.status();
        setVmState(status.state);
      } catch (err) {
        console.error('Failed to fetch status:', err);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    try {
      setError(null);
      await window.colima.start();
      setVmState('starting');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start VM';
      setError(message);
      throw err;
    }
  };

  const handleStop = async () => {
    try {
      setError(null);
      await window.colima.stop();
      setVmState('stopping');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to stop VM';
      setError(message);
      throw err;
    }
  };

  const handleRestart = async () => {
    try {
      setError(null);
      await window.colima.restart();
      setVmState('stopping');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to restart VM';
      setError(message);
      throw err;
    }
  };

  const isTransitioning = vmState === 'starting' || vmState === 'stopping';
  const isRunning = vmState === 'running';
  const isStopped = vmState === 'stopped';

  return (
    <div className="controls-panel" role="region" aria-label="VM Controls">
      <div className="controls-buttons">
        <ControlButton
          label="Start"
          onClick={handleStart}
          disabled={!isStopped || isTransitioning}
          variant="primary"
          loading={vmState === 'starting'}
        />
        <ControlButton
          label="Stop"
          onClick={handleStop}
          disabled={!isRunning || isTransitioning}
          variant="danger"
          loading={vmState === 'stopping'}
        />
        <ControlButton
          label="Restart"
          onClick={handleRestart}
          disabled={!isRunning || isTransitioning}
          variant="secondary"
          loading={isTransitioning}
        />
      </div>

      {error && (
        <div className="controls-error" role="alert">
          <strong>Error:</strong> {error}
        </div>
      )}

      {isTransitioning && (
        <div className="controls-status" role="status" aria-live="polite">
          {vmState === 'starting' && 'Starting VM...'}
          {vmState === 'stopping' && 'Stopping VM...'}
        </div>
      )}
    </div>
  );
}

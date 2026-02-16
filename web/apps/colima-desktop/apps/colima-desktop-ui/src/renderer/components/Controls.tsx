import React, { useState } from 'react';

export function Controls() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      await window.colima.start();
      setMessage('VM started successfully');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      await window.colima.stop();
      setMessage('VM stopped successfully');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleRestart = async () => {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      await window.colima.restart();
      setMessage('VM restarted successfully');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="controls">
      <div className="controls-buttons">
        <button
          className="btn btn-primary"
          onClick={handleStart}
          disabled={loading}
        >
          {loading ? 'Starting...' : 'Start'}
        </button>
        <button
          className="btn btn-danger"
          onClick={handleStop}
          disabled={loading}
        >
          {loading ? 'Stopping...' : 'Stop'}
        </button>
        <button
          className="btn btn-warning"
          onClick={handleRestart}
          disabled={loading}
        >
          {loading ? 'Restarting...' : 'Restart'}
        </button>
      </div>

      {error && <div className="controls-error">{error}</div>}
      {message && <div className="controls-message">{message}</div>}
    </div>
  );
}

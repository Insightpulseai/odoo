import React, { useState } from 'react';
import { Status } from './components/Status';
import { Controls } from './components/Controls';
import { Settings } from './components/Settings';
import { Logs } from './components/Logs';

export function App() {
  const [view, setView] = useState<'main' | 'settings' | 'logs'>('main');

  return (
    <div className="app">
      <header className="app-header">
        <h1>Colima Desktop</h1>
        <nav className="app-nav">
          <button onClick={() => setView('main')} className={view === 'main' ? 'active' : ''}>
            Status
          </button>
          <button onClick={() => setView('settings')} className={view === 'settings' ? 'active' : ''}>
            Settings
          </button>
          <button onClick={() => setView('logs')} className={view === 'logs' ? 'active' : ''}>
            Logs
          </button>
        </nav>
      </header>
      <main className="app-main">
        {view === 'main' && (
          <>
            <Status />
            <Controls />
          </>
        )}
        {view === 'settings' && <Settings />}
        {view === 'logs' && <Logs />}
      </main>
    </div>
  );
}

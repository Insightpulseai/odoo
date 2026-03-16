import React from 'react';
import { Status } from './components/Status';
import { Controls } from './components/Controls';

export function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Colima Desktop</h1>
      </header>
      <main className="app-main">
        <Status />
        <Controls />
      </main>
    </div>
  );
}

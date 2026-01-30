import React from 'react';
import ReactDOM from 'react-dom/client';
import { AIChatWidgetDemo } from '../src/react/AIChatWidget';
import { ThemeProvider, ThemeSwitcher, ThemedContainer } from '../src/react/ThemeProvider';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <ThemedContainer>
        <div style={{ padding: '20px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            paddingBottom: '20px',
            borderBottom: '1px solid var(--theme-border)'
          }}>
            <div>
              <h1 style={{ margin: 0, marginBottom: '8px' }}>InsightPulse AI Design System</h1>
              <p style={{ margin: 0, color: 'var(--theme-textSecondary)', fontSize: '14px' }}>
                Fluent 2-aligned design with multiple aesthetic systems
              </p>
            </div>
            <ThemeSwitcher />
          </div>
          <AIChatWidgetDemo />
        </div>
      </ThemedContainer>
    </ThemeProvider>
  </React.StrictMode>
);

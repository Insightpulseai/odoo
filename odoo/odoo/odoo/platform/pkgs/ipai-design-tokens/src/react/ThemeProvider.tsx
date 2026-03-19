import React, { createContext, useContext, useState, useEffect } from 'react';

// ============================================================================
// Theme System - Aesthetic Systems with Light/Dark Modes
// ============================================================================

export type AestheticSystem = 'default' | 'dull' | 'claude' | 'chatgpt' | 'gemini';
export type ColorMode = 'light' | 'dark';
export type ThemeMode = `${AestheticSystem}-${ColorMode}`;

interface ThemeContextType {
  aesthetic: AestheticSystem;
  colorMode: ColorMode;
  themeMode: ThemeMode;
  setTheme: (aesthetic: AestheticSystem, colorMode: ColorMode) => void;
  toggleColorMode: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

// ============================================================================
// Theme Definitions (4 Aesthetics × 2 Modes = 8 Themes)
// ============================================================================

export const themes = {
  // ========== DEFAULT AESTHETIC (Current InsightPulse AI) ==========
  'default-light': {
    name: 'Default Light',
    aesthetic: 'Default',
    mode: 'Light',
    description: 'Bright, clean InsightPulse aesthetic',
    colors: {
      background: '#ffffff',
      surface: '#f5f5f5',
      surfaceElevated: '#ffffff',
      text: '#1a1a1a',
      textSecondary: '#5c5c5c',
      textTertiary: '#a0a0a0',
      border: '#e0e0e0',
      primary: '#0073e6',
      primaryHover: '#005bb3',
      aiAccent: '#7c3aed',
      aiAccentLight: '#ede9fe',
    },
  },

  'default-dark': {
    name: 'Default Dark',
    aesthetic: 'Default',
    mode: 'Dark',
    description: 'High contrast, modern dark theme',
    colors: {
      background: '#0d0d0d',
      surface: '#1a1a1a',
      surfaceElevated: '#2d2d2d',
      text: '#ffffff',
      textSecondary: '#c2c2c2',
      textTertiary: '#7a7a7a',
      border: '#3d3d3d',
      primary: '#4da6ff',
      primaryHover: '#80bfff',
      aiAccent: '#a78bfa',
      aiAccentLight: '#2d1b69',
    },
  },

  // ========== DULL AESTHETIC (Soft, low contrast) ==========
  'dull-light': {
    name: 'Dull Light',
    aesthetic: 'Dull',
    mode: 'Light',
    description: 'Soft, low-contrast, easy on eyes',
    colors: {
      background: '#e8e8e8',
      surface: '#d6d6d6',
      surfaceElevated: '#ececec',
      text: '#3d3d3d',
      textSecondary: '#5c5c5c',
      textTertiary: '#7a7a7a',
      border: '#c2c2c2',
      primary: '#5c8fb3',
      primaryHover: '#4d7a99',
      aiAccent: '#8b7aa3',
      aiAccentLight: '#d4cce0',
    },
  },

  'dull-dark': {
    name: 'Dull Dark',
    aesthetic: 'Dull',
    mode: 'Dark',
    description: 'Muted dark, reduced eye strain',
    colors: {
      background: '#1a1a1a',
      surface: '#2d2d2d',
      surfaceElevated: '#3d3d3d',
      text: '#c2c2c2',
      textSecondary: '#a0a0a0',
      textTertiary: '#7a7a7a',
      border: '#4d4d4d',
      primary: '#6b9ec7',
      primaryHover: '#82b0d4',
      aiAccent: '#9d8db3',
      aiAccentLight: '#3d3347',
    },
  },

  // ========== CLAUDE AESTHETIC (Warm, sophisticated) ==========
  'claude-light': {
    name: 'Claude Light',
    aesthetic: 'Claude',
    mode: 'Light',
    description: 'Warm, sophisticated, paper-like',
    colors: {
      background: '#faf9f7',
      surface: '#f4f3f1',
      surfaceElevated: '#ffffff',
      text: '#2d2d2d',
      textSecondary: '#6b6b6b',
      textTertiary: '#9b9b9b',
      border: '#e5e3df',
      primary: '#d97706',
      primaryHover: '#b45309',
      aiAccent: '#8b5cf6',
      aiAccentLight: '#f3e8ff',
    },
  },

  'claude-dark': {
    name: 'Claude Dark',
    aesthetic: 'Claude',
    mode: 'Dark',
    description: 'Warm dark, sophisticated depth',
    colors: {
      background: '#1a1714',
      surface: '#2d2a26',
      surfaceElevated: '#3d3a36',
      text: '#f4f3f1',
      textSecondary: '#c2bfba',
      textTertiary: '#8b8782',
      border: '#4d4a46',
      primary: '#f59e0b',
      primaryHover: '#fbbf24',
      aiAccent: '#a78bfa',
      aiAccentLight: '#3d2b5f',
    },
  },

  // ========== CHATGPT AESTHETIC (Cool, professional) ==========
  'chatgpt-light': {
    name: 'ChatGPT Light',
    aesthetic: 'ChatGPT',
    mode: 'Light',
    description: 'Cool, professional, minimal',
    colors: {
      background: '#f7f7f8',
      surface: '#ffffff',
      surfaceElevated: '#ffffff',
      text: '#2d2d2d',
      textSecondary: '#6e6e80',
      textTertiary: '#acacbe',
      border: '#e0e0e0',
      primary: '#10a37f',
      primaryHover: '#0d8968',
      aiAccent: '#ab68ff',
      aiAccentLight: '#f3e8ff',
    },
  },

  'chatgpt-dark': {
    name: 'ChatGPT Dark',
    aesthetic: 'ChatGPT',
    mode: 'Dark',
    description: 'Cool dark, professional depth',
    colors: {
      background: '#171717',
      surface: '#2d2d2d',
      surfaceElevated: '#3d3d3d',
      text: '#ececf1',
      textSecondary: '#c5c5d2',
      textTertiary: '#8e8ea0',
      border: '#4d4d57',
      primary: '#19c37d',
      primaryHover: '#1fd99a',
      aiAccent: '#c77dff',
      aiAccentLight: '#3d2b5f',
    },
  },

  // ========== GEMINI AESTHETIC (Gradient, playful) ==========
  'gemini-light': {
    name: 'Gemini Light',
    aesthetic: 'Gemini',
    mode: 'Light',
    description: 'Bright, colorful, Google-inspired',
    colors: {
      background: '#f8f9fa',
      surface: '#ffffff',
      surfaceElevated: '#ffffff',
      text: '#1f1f1f',
      textSecondary: '#5f6368',
      textTertiary: '#9aa0a6',
      border: '#e8eaed',
      primary: '#1a73e8',
      primaryHover: '#1557b0',
      aiAccent: '#8430ce',
      aiAccentLight: '#f3e8ff',
    },
  },

  'gemini-dark': {
    name: 'Gemini Dark',
    aesthetic: 'Gemini',
    mode: 'Dark',
    description: 'Dark gradient, playful depth',
    colors: {
      background: '#131314',
      surface: '#1f1f1f',
      surfaceElevated: '#2d2d2d',
      text: '#e8eaed',
      textSecondary: '#bdc1c6',
      textTertiary: '#80868b',
      border: '#3c4043',
      primary: '#4285f4',
      primaryHover: '#669df6',
      aiAccent: '#a142f4',
      aiAccentLight: '#3d2b5f',
    },
  },
};

// ============================================================================
// Theme Provider Component
// ============================================================================

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [aesthetic, setAesthetic] = useState<AestheticSystem>(() => {
    const stored = localStorage.getItem('ipai-aesthetic');
    return (stored as AestheticSystem) || 'default';
  });

  const [colorMode, setColorMode] = useState<ColorMode>(() => {
    const stored = localStorage.getItem('ipai-color-mode');
    return (stored as ColorMode) || 'light';
  });

  const themeMode: ThemeMode = `${aesthetic}-${colorMode}`;

  useEffect(() => {
    localStorage.setItem('ipai-aesthetic', aesthetic);
    localStorage.setItem('ipai-color-mode', colorMode);

    // Apply CSS variables to document root
    const theme = themes[themeMode];
    const root = document.documentElement;

    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--theme-${key}`, value);
    });
  }, [aesthetic, colorMode, themeMode]);

  const setTheme = (newAesthetic: AestheticSystem, newColorMode: ColorMode) => {
    setAesthetic(newAesthetic);
    setColorMode(newColorMode);
  };

  const toggleColorMode = () => {
    setColorMode(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ aesthetic, colorMode, themeMode, setTheme, toggleColorMode }}>
      {children}
    </ThemeContext.Provider>
  );
};

// ============================================================================
// Theme Switcher Component
// ============================================================================

export const ThemeSwitcher: React.FC = () => {
  const { aesthetic, colorMode, themeMode, setTheme, toggleColorMode } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  const aestheticOptions: { value: AestheticSystem; label: string; emoji: string }[] = [
    { value: 'default', label: 'Default', emoji: '🎨' },
    { value: 'dull', label: 'Dull', emoji: '🌫️' },
    { value: 'claude', label: 'Claude', emoji: '📜' },
    { value: 'chatgpt', label: 'ChatGPT', emoji: '💬' },
    { value: 'gemini', label: 'Gemini', emoji: '✨' },
  ];

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      {/* Aesthetic Selector */}
      <div style={{ position: 'relative' }}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          style={{
            padding: '8px 16px',
            backgroundColor: 'var(--theme-surface)',
            color: 'var(--theme-text)',
            border: `1px solid var(--theme-border)`,
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s ease',
          }}
        >
          {aestheticOptions.find(opt => opt.value === aesthetic)?.emoji} {themes[themeMode].aesthetic}
          <span style={{ fontSize: '10px' }}>▼</span>
        </button>

        {isOpen && (
          <div
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              marginTop: '8px',
              backgroundColor: 'var(--theme-surfaceElevated)',
              border: `1px solid var(--theme-border)`,
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              padding: '8px',
              minWidth: '200px',
              zIndex: 1000,
            }}
          >
            {aestheticOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => {
                  setTheme(option.value, colorMode);
                  setIsOpen(false);
                }}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  backgroundColor: aesthetic === option.value ? 'var(--theme-primary)' : 'transparent',
                  color: aesthetic === option.value ? '#ffffff' : 'var(--theme-text)',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  fontSize: '14px',
                  transition: 'all 0.2s ease',
                  marginBottom: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
                onMouseEnter={(e) => {
                  if (aesthetic !== option.value) {
                    e.currentTarget.style.backgroundColor = 'var(--theme-surface)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (aesthetic !== option.value) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }
                }}
              >
                <span>{option.emoji}</span>
                <div>
                  <div style={{ fontWeight: 600 }}>{option.label}</div>
                  <div style={{ fontSize: '12px', opacity: 0.7, marginTop: '2px' }}>
                    {themes[`${option.value}-${colorMode}`].description}
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Light/Dark Toggle */}
      <button
        onClick={toggleColorMode}
        style={{
          padding: '8px 16px',
          backgroundColor: 'var(--theme-surface)',
          color: 'var(--theme-text)',
          border: `1px solid var(--theme-border)`,
          borderRadius: '8px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          transition: 'all 0.2s ease',
        }}
        title={`Switch to ${colorMode === 'light' ? 'dark' : 'light'} mode`}
      >
        {colorMode === 'light' ? '🌙' : '☀️'}
        <span style={{ textTransform: 'capitalize' }}>{colorMode}</span>
      </button>
    </div>
  );
};

// ============================================================================
// Themed Container Component
// ============================================================================

export const ThemedContainer: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({
  children,
  style = {}
}) => {
  return (
    <div
      style={{
        backgroundColor: 'var(--theme-background)',
        color: 'var(--theme-text)',
        minHeight: '100vh',
        transition: 'background-color 0.3s ease, color 0.3s ease',
        ...style,
      }}
    >
      {children}
    </div>
  );
};

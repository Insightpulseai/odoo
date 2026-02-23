import React, { useState } from 'react';
import { KineticScene } from '../components/webgl/KineticScene';
import { ImageUploadOverlay } from '../components/ui/ImageUploadOverlay';
import { CameraConfigOverlay } from '../components/ui/CameraConfigOverlay';
import { ControlPanel } from '../components/ui/ControlPanel';
import { useTextureManager } from '../hooks/useTextureManager';

const isDev = import.meta.env.DEV;

const SERVICES = [
  {
    label: 'Video Production',
    desc: 'Broadcast-ready studios with full lighting rigs',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M15 10l4.553-2.069A1 1 0 0121 8.882v6.236a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h10a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z"/>
      </svg>
    ),
  },
  {
    label: 'Photography',
    desc: 'Cyclorama, seamless paper, and controlled lighting',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
        <circle cx="12" cy="13" r="4"/>
      </svg>
    ),
  },
  {
    label: 'Events & Presentations',
    desc: 'Configurable layouts for launches and screenings',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>
      </svg>
    ),
  },
  {
    label: 'Studio Rental',
    desc: 'Hourly and half-day rates for independent creators',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
    ),
  },
];

export default function Landing() {
  const {
    displayState,
    marqueeState,
    animationSpeeds,
    updateDisplayImage,
    updateMarqueeImage,
    resetToDefaults,
    updateAnimationSpeed,
  } = useTextureManager();

  const [cameraInfo, setCameraInfo] = useState(null);

  return (
    <>
      {/* ── HERO — full-viewport 3D scene ── */}
      <div style={{ position: 'relative', height: '100vh', width: '100%' }}>

        <KineticScene
          displayTexture={displayState.texture}
          displayDimensions={displayState.dimensions}
          isDisplayLoading={displayState.isLoading}
          marqueeTexture={marqueeState.texture}
          isMarqueeLoading={marqueeState.isLoading}
          animationSpeed={animationSpeeds}
          onCameraUpdate={setCameraInfo}
        />

        {/* Loading badge */}
        {(displayState.isLoading || marqueeState.isLoading) && (
          <div style={{
            position: 'absolute', top: '80px', right: '24px',
            background: 'rgba(0,0,0,0.7)', border: '1px solid rgba(255,255,255,0.12)',
            backdropFilter: 'blur(8px)', borderRadius: '6px',
            padding: '8px 14px', display: 'flex', alignItems: 'center',
            gap: '8px', fontSize: '12px', color: 'rgba(255,255,255,0.6)',
            fontFamily: "'Inter', sans-serif",
          }}>
            <span style={{
              display: 'inline-block', width: '12px', height: '12px',
              border: '2px solid rgba(255,255,255,0.2)', borderTopColor: '#fff',
              borderRadius: '50%', animation: 'spin 0.8s linear infinite',
            }} />
            Loading
          </div>
        )}

        {/* Dev-only overlays */}
        {isDev && (
          <>
            <ImageUploadOverlay
              displayImage={displayState.image}
              marqueeImage={marqueeState.image}
              onDisplayImageChange={updateDisplayImage}
              onMarqueeImageChange={updateMarqueeImage}
              onResetToDefaults={resetToDefaults}
              isLoading={displayState.isLoading || marqueeState.isLoading}
              className="absolute top-20 left-4 z-40 w-60"
            />
            <CameraConfigOverlay cameraInfo={cameraInfo} className="absolute bottom-20 left-4 z-40 w-60" />
            <ControlPanel
              onResetToDefaults={resetToDefaults}
              animationSpeeds={animationSpeeds}
              onAnimationSpeedChange={updateAnimationSpeed}
              isLoading={displayState.isLoading || marqueeState.isLoading}
              cameraInfo={cameraInfo}
            />
          </>
        )}

        {/* Hero footer bar */}
        <div style={{
          position: 'absolute', bottom: 0, left: 0, right: 0,
          background: 'linear-gradient(to top, rgba(0,0,0,0.85) 0%, transparent 100%)',
          padding: '60px 40px 32px',
          display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between',
          pointerEvents: 'none',
        }}>
          <div>
            <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: '11px', fontWeight: '600', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: '6px', fontFamily: "'Inter', sans-serif" }}>
              Premium Production Studio
            </p>
            <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '13px', fontFamily: "'Inter', sans-serif" }}>
              La Fuerza Plaza · Makati City
            </p>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '5px', opacity: 0.35 }}>
            <span style={{ color: '#fff', fontSize: '10px', letterSpacing: '0.12em', textTransform: 'uppercase', fontFamily: "'Inter', sans-serif" }}>Scroll</span>
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <path d="M8 3v10M3 9l5 5 5-5" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </div>
      </div>

      {/* ── SERVICES STRIP ── */}
      <section id="rentals" style={{ borderTop: '1px solid rgba(255,255,255,0.08)', borderBottom: '1px solid rgba(255,255,255,0.08)', background: '#0a0a0a' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)' }}>
          {SERVICES.map((svc, i) => (
            <div
              key={svc.label}
              style={{ padding: '36px 32px', borderRight: i < 3 ? '1px solid rgba(255,255,255,0.08)' : 'none', transition: 'background 0.2s', cursor: 'default' }}
              onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.03)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
            >
              <div style={{ color: 'rgba(255,255,255,0.35)', marginBottom: '14px' }}>{svc.icon}</div>
              <p style={{ color: '#fafafa', fontSize: '14px', fontWeight: '600', marginBottom: '6px', fontFamily: "'Inter', sans-serif" }}>{svc.label}</p>
              <p style={{ color: '#71717a', fontSize: '13px', lineHeight: '1.55', fontFamily: "'Inter', sans-serif" }}>{svc.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </>
  );
}

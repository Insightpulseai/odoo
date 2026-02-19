import React from 'react';

export default function Gallery() {
  return (
    <main style={{ minHeight: '100vh', background: '#000', paddingTop: '64px', fontFamily: "'Inter', sans-serif" }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '80px 40px' }}>
        <p style={{ color: '#52525b', fontSize: '11px', fontWeight: '600', letterSpacing: '0.14em', textTransform: 'uppercase', marginBottom: '12px' }}>
          Our Work
        </p>
        <h1 style={{ color: '#fafafa', fontSize: 'clamp(36px, 5vw, 56px)', fontFamily: "'Playfair Display', serif", fontWeight: '700', margin: '0 0 60px', lineHeight: 1.1 }}>
          Gallery
        </h1>
        {/* Gallery grid goes here */}
        <div style={{ color: '#3f3f46', fontSize: '14px', border: '1px dashed #27272a', borderRadius: '12px', padding: '80px', textAlign: 'center' }}>
          Studio photos coming soon
        </div>
      </div>
    </main>
  );
}

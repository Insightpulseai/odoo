import React from 'react';
import { BookingSection } from '../components/ui/BookingSection';

export default function Booking() {
  return (
    <main style={{ background: '#000', paddingTop: '64px' }}>
      <BookingSection />

      {/* Footer */}
      <footer style={{
        background: '#000',
        borderTop: '1px solid rgba(255,255,255,0.08)',
        padding: '40px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px',
        fontFamily: "'Inter', sans-serif",
      }}>
        <div>
          <p style={{ color: '#52525b', fontSize: '12px', marginBottom: '2px' }}>
            La Fuerza Plaza, 2241 Chino Roces Ave, Makati City
          </p>
          <a href="mailto:business@w9studio.net" style={{ color: '#52525b', fontSize: '12px', textDecoration: 'none' }}>
            business@w9studio.net
          </a>
        </div>
        <p style={{ color: '#52525b', fontSize: '12px', margin: 0 }}>
          © {new Date().getFullYear()} W9 Studio. All rights reserved.
        </p>
      </footer>
    </main>
  );
}

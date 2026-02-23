import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Reset scroll indicator when route changes
  useEffect(() => {
    setScrolled(false);
  }, [location.pathname]);

  const NAV_ITEMS = [
    { label: 'Home',     to: '/'         },
    { label: 'Gallery',  to: '/gallery'  },
    { label: 'Rentals',  to: '/rentals'  },
    { label: 'About',    to: '/about'    },
    { label: 'Book Now', to: '/booking'  },
  ];

  const btnStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '36px',
    padding: '0 20px',
    borderRadius: '9999px',
    background: '#fff',
    color: '#09090b',
    fontSize: '13px',
    fontWeight: '600',
    letterSpacing: '0.025em',
    lineHeight: 1,
    textDecoration: 'none',
    whiteSpace: 'nowrap',
    transition: 'opacity 0.2s',
  };

  return (
    <nav style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 100,
      height: '64px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'flex-start',
      padding: '0 36px',
      gap: '10px',
      background: scrolled ? 'rgba(0,0,0,0.88)' : 'transparent',
      backdropFilter: scrolled ? 'blur(16px)' : 'none',
      borderBottom: scrolled ? '1px solid rgba(255,255,255,0.08)' : 'none',
      transition: 'background 0.3s, backdrop-filter 0.3s, border-color 0.3s',
      fontFamily: "'Inter', sans-serif",
    }}>
      {NAV_ITEMS.map(({ label, to }) => (
        <Link
          key={label}
          to={to}
          style={{
            ...btnStyle,
            opacity: location.pathname === to ? 0.6 : 1,
          }}
          onMouseEnter={e => (e.currentTarget.style.opacity = '0.82')}
          onMouseLeave={e => (e.currentTarget.style.opacity = location.pathname === to ? '0.6' : '1')}
        >
          {label}
        </Link>
      ))}
    </nav>
  );
}

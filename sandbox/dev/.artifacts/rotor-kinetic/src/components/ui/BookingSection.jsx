import React, { useState } from 'react';
import { DayPicker } from 'react-day-picker';
import 'react-day-picker/dist/style.css';

/* ─── Design tokens ─────────────────────────────── */
const T = {
  bg: '#000000',
  surface1: '#0f0f0f',
  surface2: '#18181b',
  surface3: '#27272a',
  border: 'rgba(255,255,255,0.1)',
  borderActive: 'rgba(255,255,255,0.45)',
  text: '#fafafa',
  textMuted: '#a1a1aa',
  textSubtle: '#71717a',
  ctaBg: '#fafafa',
  ctaText: '#09090b',
  headingFont: "'Playfair Display', serif",
  bodyFont: "'Inter', sans-serif",
};

const TIME_SLOTS = [
  '8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM',
  '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM',
  '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM',
];

const STUDIO_TYPES = [
  { id: 'video', label: 'Video Production' },
  { id: 'photo', label: 'Photography' },
  { id: 'event', label: 'Event / Presentation' },
  { id: 'rental', label: 'Studio Rental Only' },
];

export function BookingSection() {
  const [selected, setSelected] = useState(undefined);
  const [timeSlot, setTimeSlot] = useState('');
  const [studioType, setStudioType] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', phone: '', message: '' });

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  /* ─── Shared input style ── */
  const inputStyle = {
    width: '100%',
    background: T.surface2,
    border: `1px solid ${T.border}`,
    borderRadius: '8px',
    padding: '11px 14px',
    color: T.text,
    fontSize: '14px',
    fontFamily: T.bodyFont,
    outline: 'none',
    boxSizing: 'border-box',
    transition: 'border-color 0.18s',
  };

  const labelStyle = {
    display: 'block',
    fontSize: '11px',
    fontWeight: '600',
    color: T.textSubtle,
    letterSpacing: '0.1em',
    textTransform: 'uppercase',
    marginBottom: '8px',
    fontFamily: T.bodyFont,
  };

  return (
    <>
      {/* ═══ BOOKING SECTION ═════════════════════════════════════════ */}
      <section
        id="booking"
        style={{
          background: T.bg,
          borderTop: `1px solid ${T.border}`,
          padding: '100px 40px',
          fontFamily: T.bodyFont,
        }}
      >
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>

          {/* Header */}
          <p style={{
            color: T.textSubtle,
            fontSize: '11px',
            fontWeight: '600',
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            marginBottom: '12px',
            fontFamily: T.bodyFont,
          }}>
            Reserve Your Session
          </p>
          <h2 style={{
            color: T.text,
            fontSize: 'clamp(36px, 5vw, 52px)',
            fontWeight: '700',
            fontFamily: T.headingFont,
            margin: '0 0 10px',
            lineHeight: 1.1,
            letterSpacing: '-0.01em',
          }}>
            Book a Studio
          </h2>
          <p style={{ color: T.textMuted, fontSize: '15px', margin: '0 0 60px', fontWeight: '400' }}>
            La Fuerza Plaza, 2241 Chino Roces Ave, Makati City
          </p>

          {/* ─── Success state ─── */}
          {submitted ? (
            <div style={{
              textAlign: 'center',
              padding: '80px 40px',
              border: `1px solid ${T.border}`,
              borderRadius: '16px',
              background: T.surface1,
            }}>
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none" style={{ margin: '0 auto 20px', display: 'block' }}>
                <circle cx="20" cy="20" r="19" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5" />
                <path d="M13 20.5l5 5 9-9" stroke="#fafafa" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <h3 style={{ color: T.text, fontSize: '26px', fontWeight: '600', fontFamily: T.headingFont, margin: '0 0 10px' }}>
                Booking Request Sent
              </h3>
              <p style={{ color: T.textMuted, fontSize: '15px', margin: 0 }}>
                We'll confirm your session via email within 24 hours.
              </p>
            </div>
          ) : (
            /* ─── Form grid ─── */
            <form onSubmit={handleSubmit}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '48px',
                alignItems: 'start',
              }}>

                {/* LEFT — Calendar + Time */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '36px' }}>

                  {/* Studio type */}
                  <div>
                    <label style={labelStyle}>Studio Type</label>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                      {STUDIO_TYPES.map(s => (
                        <button
                          key={s.id}
                          type="button"
                          onClick={() => setStudioType(s.id)}
                          style={{
                            padding: '11px 14px',
                            borderRadius: '8px',
                            border: studioType === s.id
                              ? `1px solid ${T.borderActive}`
                              : `1px solid ${T.border}`,
                            background: studioType === s.id ? T.surface3 : T.surface1,
                            color: studioType === s.id ? T.text : T.textMuted,
                            fontSize: '13px',
                            fontWeight: '500',
                            cursor: 'pointer',
                            fontFamily: T.bodyFont,
                            transition: 'all 0.18s',
                            textAlign: 'left',
                          }}
                        >
                          {s.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Calendar */}
                  <div>
                    <label style={labelStyle}>Select Date</label>
                    <div style={{
                      background: T.surface1,
                      border: `1px solid ${T.border}`,
                      borderRadius: '12px',
                      padding: '16px',
                      width: '100%',
                      boxSizing: 'border-box',
                    }}>
                      <style>{`
                        .rdp {
                          --rdp-accent-color: #fafafa;
                          --rdp-background-color: rgba(255,255,255,0.08);
                          margin: 0;
                        }
                        .rdp-day { color: rgba(255,255,255,0.7); border-radius: 6px; font-size: 13px; }
                        .rdp-day_today { color: #fff; font-weight: 700; text-decoration: underline; text-underline-offset: 3px; }
                        .rdp-head_cell { color: rgba(255,255,255,0.3); font-size: 11px; font-weight: 600; letter-spacing: 0.06em; }
                        .rdp-caption_label { color: #fff; font-family: 'Playfair Display', serif; font-size: 15px; font-weight: 600; }
                        .rdp-nav_button { color: rgba(255,255,255,0.4); }
                        .rdp-nav_button:hover { color: #fff !important; background: rgba(255,255,255,0.08) !important; }
                        .rdp-day_selected { background: #fafafa !important; color: #09090b !important; font-weight: 700; }
                        .rdp-day:hover:not(.rdp-day_selected):not(.rdp-day_disabled) { background: rgba(255,255,255,0.08) !important; }
                        .rdp-day_disabled { color: rgba(255,255,255,0.2) !important; cursor: default; }
                      `}</style>
                      <DayPicker
                        mode="single"
                        selected={selected}
                        onSelect={setSelected}
                        disabled={{ before: new Date() }}
                      />
                    </div>
                  </div>

                  {/* Time slots */}
                  <div>
                    <label style={labelStyle}>Select Time</label>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '6px' }}>
                      {TIME_SLOTS.map(t => (
                        <button
                          key={t}
                          type="button"
                          onClick={() => setTimeSlot(t)}
                          style={{
                            padding: '8px 4px',
                            borderRadius: '6px',
                            border: timeSlot === t ? `1px solid ${T.borderActive}` : `1px solid ${T.border}`,
                            background: timeSlot === t ? T.surface3 : T.surface1,
                            color: timeSlot === t ? T.text : T.textMuted,
                            fontSize: '12px',
                            fontWeight: '500',
                            cursor: 'pointer',
                            fontFamily: T.bodyFont,
                            transition: 'all 0.18s',
                          }}
                        >
                          {t}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* RIGHT — Contact form */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>

                  <div>
                    <label style={labelStyle}>Full Name</label>
                    <input
                      required
                      placeholder="Juan dela Cruz"
                      style={inputStyle}
                      value={form.name}
                      onChange={e => setForm({ ...form, name: e.target.value })}
                      onFocus={e => (e.target.style.borderColor = T.borderActive)}
                      onBlur={e => (e.target.style.borderColor = T.border)}
                    />
                  </div>

                  <div>
                    <label style={labelStyle}>Email Address</label>
                    <input
                      required
                      type="email"
                      placeholder="you@example.com"
                      style={inputStyle}
                      value={form.email}
                      onChange={e => setForm({ ...form, email: e.target.value })}
                      onFocus={e => (e.target.style.borderColor = T.borderActive)}
                      onBlur={e => (e.target.style.borderColor = T.border)}
                    />
                  </div>

                  <div>
                    <label style={labelStyle}>Phone Number</label>
                    <input
                      placeholder="+63 9XX XXX XXXX"
                      style={inputStyle}
                      value={form.phone}
                      onChange={e => setForm({ ...form, phone: e.target.value })}
                      onFocus={e => (e.target.style.borderColor = T.borderActive)}
                      onBlur={e => (e.target.style.borderColor = T.border)}
                    />
                  </div>

                  <div>
                    <label style={labelStyle}>Project Details</label>
                    <textarea
                      rows={5}
                      placeholder="Tell us about your project — type of shoot, crew size, equipment needs..."
                      style={{ ...inputStyle, resize: 'vertical', lineHeight: '1.6' }}
                      value={form.message}
                      onChange={e => setForm({ ...form, message: e.target.value })}
                      onFocus={e => (e.target.style.borderColor = T.borderActive)}
                      onBlur={e => (e.target.style.borderColor = T.border)}
                    />
                  </div>

                  {/* Booking summary */}
                  {(selected || timeSlot || studioType) && (
                    <div style={{
                      background: T.surface2,
                      border: `1px solid ${T.border}`,
                      borderRadius: '10px',
                      padding: '14px 16px',
                      fontSize: '13px',
                      color: T.textMuted,
                      lineHeight: '1.7',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '2px',
                    }}>
                      {studioType && (
                        <span>{STUDIO_TYPES.find(s => s.id === studioType)?.label}</span>
                      )}
                      {selected && (
                        <span>{selected.toLocaleDateString('en-PH', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
                      )}
                      {timeSlot && <span>{timeSlot}</span>}
                    </div>
                  )}

                  {/* Submit */}
                  <button
                    type="submit"
                    style={{
                      background: T.ctaBg,
                      color: T.ctaText,
                      border: 'none',
                      borderRadius: '8px',
                      padding: '14px',
                      fontSize: '14px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      fontFamily: T.bodyFont,
                      letterSpacing: '0.02em',
                      transition: 'opacity 0.2s',
                      width: '100%',
                    }}
                    onMouseEnter={e => (e.target.style.opacity = '0.88')}
                    onMouseLeave={e => (e.target.style.opacity = '1')}
                  >
                    Request Booking
                  </button>

                  <p style={{ color: T.textSubtle, fontSize: '12px', textAlign: 'center', margin: 0 }}>
                    We'll confirm within 24 hours via email.
                  </p>
                </div>
              </div>
            </form>
          )}
        </div>
      </section>

      {/* ═══ MAP SECTION ════════════════════════════════════════════ */}
      <section
        id="location"
        style={{
          background: T.surface1,
          borderTop: `1px solid ${T.border}`,
          fontFamily: T.bodyFont,
        }}
      >
        {/* Label row */}
        <div style={{
          maxWidth: '1100px',
          margin: '0 auto',
          padding: '48px 40px 32px',
          display: 'flex',
          alignItems: 'flex-end',
          justifyContent: 'space-between',
          gap: '24px',
          flexWrap: 'wrap',
        }}>
          <div>
            <p style={{
              color: T.textSubtle,
              fontSize: '11px',
              fontWeight: '600',
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              marginBottom: '8px',
            }}>
              Find Us
            </p>
            <h3 style={{
              color: T.text,
              fontSize: '24px',
              fontWeight: '600',
              fontFamily: T.headingFont,
              margin: 0,
              letterSpacing: '-0.01em',
            }}>
              La Fuerza Plaza, Makati
            </h3>
            <p style={{ color: T.textMuted, fontSize: '14px', marginTop: '6px' }}>
              2241 Chino Roces Ave, Makati City, Metro Manila
            </p>
          </div>
          <a
            href="https://maps.google.com/?q=La+Fuerza+Plaza+2241+Chino+Roces+Ave+Makati+City"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              color: T.textMuted,
              textDecoration: 'none',
              fontSize: '13px',
              fontWeight: '500',
              border: `1px solid ${T.border}`,
              borderRadius: '6px',
              padding: '8px 14px',
              transition: 'border-color 0.2s, color 0.2s',
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = T.borderActive; e.currentTarget.style.color = T.text; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = T.border; e.currentTarget.style.color = T.textMuted; }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            Open in Maps
          </a>
        </div>

        {/* Map embed */}
        <div style={{ width: '100%', height: '380px', overflow: 'hidden' }}>
          <iframe
            title="W9 Studio Location"
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3861.9!2d121.017!3d14.553!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3397c92b68281f0d%3A0x1e46c7c95a45b3db!2sLa%20Fuerza%20Plaza%2C%202241%20Chino%20Roces%20Ave%2C%20Makati%2C%20Metro%20Manila!5e0!3m2!1sen!2sph!4v1708000000000!5m2!1sen!2sph"
            width="100%"
            height="380"
            style={{ border: 0, display: 'block', filter: 'grayscale(100%) invert(92%) contrast(90%)' }}
            allowFullScreen
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
          />
        </div>
      </section>
    </>
  );
}

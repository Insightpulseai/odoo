import { supabase } from './supabase';

export interface BookingPayload {
  name: string;
  email: string;
  phone: string;
  message: string;
  studio_type: string;
  booking_date: string; // ISO date string YYYY-MM-DD
  time_slot: string;
}

export interface BookingResult {
  success: boolean;
  error?: string;
}

/**
 * Insert a new booking request into Supabase.
 * Table: public.bookings
 * RLS: INSERT allowed for anon (status defaults to 'pending').
 */
export async function submitBooking(payload: BookingPayload): Promise<BookingResult> {
  const { error } = await supabase.from('bookings').insert([
    {
      name: payload.name.trim(),
      email: payload.email.trim().toLowerCase(),
      phone: payload.phone.trim() || null,
      message: payload.message.trim() || null,
      studio_type: payload.studio_type,
      booking_date: payload.booking_date,
      time_slot: payload.time_slot,
      status: 'pending',
    },
  ]);

  if (error) {
    console.error('[bookings] insert error:', error);
    return { success: false, error: error.message };
  }

  return { success: true };
}

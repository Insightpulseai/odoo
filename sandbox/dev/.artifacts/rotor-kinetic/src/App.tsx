import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/ui/Navbar';
import Landing from './pages/Landing';
import Gallery from './pages/Gallery';
import Rentals from './pages/Rentals';
import About from './pages/About';
import Booking from './pages/Booking';

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/"        element={<Landing />} />
        <Route path="/gallery" element={<Gallery />} />
        <Route path="/rentals" element={<Rentals />} />
        <Route path="/about"   element={<About />} />
        <Route path="/booking" element={<Booking />} />
      </Routes>
    </BrowserRouter>
  );
}

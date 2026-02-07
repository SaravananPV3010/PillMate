import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import '@/App.css';
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';
import MedicationsPage from './pages/MedicationsPage';
import { Toaster } from '@/components/ui/sonner';

const Navigation = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="backdrop-blur-xl bg-white/80 border-b border-stone-100/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-sage rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-xl">💊</span>
            </div>
            <span className="font-fraunces text-2xl font-semibold text-sage">PillGuide</span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-stone-700 hover:text-sage transition-colors duration-300 font-jakarta font-medium">
              Home
            </Link>
            <Link to="/upload" className="text-stone-700 hover:text-sage transition-colors duration-300 font-jakarta font-medium">
              Upload Prescription
            </Link>
            <Link to="/medications" className="text-stone-700 hover:text-sage transition-colors duration-300 font-jakarta font-medium">
              My Medications
            </Link>
          </div>

          <button
            data-testid="mobile-menu-button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-sage"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden pb-4 space-y-3" data-testid="mobile-menu">
            <Link to="/" className="block text-stone-700 hover:text-sage transition-colors duration-300 font-jakarta font-medium">
              Home
            </Link>
            <Link to="/upload" className="block text-stone-700 hover:text-sage transition-colors duration-300 font-jakarta font-medium">
              Upload Prescription
            </Link>
            <Link to="/medications" className="block text-stone-700 hover:text-sage transition-colors duration-300 font-jakarta font-medium">
              My Medications
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/medications" element={<MedicationsPage />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-center" richColors />
    </div>
  );
}

export default App;
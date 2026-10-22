import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Box } from 'lucide-react';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <Link to="/" className="nav-brand">
        <div className="brand-icon"><Box size={20} color="white" /></div>
        <span>AR Review</span>
      </Link>
      
      <div className={`nav-links ${menuOpen ? 'open' : ''}`}>
        <Link to="/" className={location.pathname === '/' ? 'active' : ''} onClick={() => setMenuOpen(false)}>Home</Link>
        <Link to="/catalog" className={location.pathname === '/catalog' ? 'active' : ''} onClick={() => setMenuOpen(false)}>Products</Link>
        <Link to="/scanner" className={location.pathname === '/scanner' ? 'active' : ''} onClick={() => setMenuOpen(false)}>QR Scanner</Link>
        <Link to="/scanner" className="nav-cta" onClick={() => setMenuOpen(false)}>📷 Scan Now</Link>
      </div>

      <button className="nav-toggle" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">
        <span></span><span></span><span></span>
      </button>
    </nav>
  );
}

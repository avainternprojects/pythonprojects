import { Link } from 'react-router-dom';
import { Box } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-brand">
          <div className="nav-brand">
            <div className="brand-icon"><Box size={20} color="white" /></div>
            <span>AR Review</span>
          </div>
          <p>Experience products in augmented reality before you buy. Read reviews, view 3D models, and make informed decisions.</p>
        </div>
        
        <div className="footer-col">
          <h4>Pages</h4>
          <Link to="/">Home</Link>
          <Link to="/catalog">Products</Link>
          <Link to="/scanner">QR Scanner</Link>
        </div>
        
        <div className="footer-col">
          <h4>Categories</h4>
          <Link to="/catalog?cat=Electronics">Electronics</Link>
          <Link to="/catalog?cat=Furniture">Furniture</Link>
          <Link to="/catalog?cat=Home Décor">Home Décor</Link>
        </div>
        
        <div className="footer-col">
          <h4>About</h4>
          <a href="#">AR Technology</a>
          <a href="#">How It Works</a>
          <a href="#">Contact</a>
        </div>
      </div>
      <div className="footer-bottom">
        <p>© 2026 AR Product Review System. Built with React, Three.js & Model-Viewer.</p>
      </div>
    </footer>
  );
}

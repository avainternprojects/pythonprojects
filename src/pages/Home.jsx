import { Link } from 'react-router-dom';
import { PRODUCTS } from '../data';
import ProductCard from '../components/ProductCard';

export default function Home() {
  const featured = [...PRODUCTS].sort((a, b) => b.rating - a.rating).slice(0, 4);

  return (
    <>
      {/* HERO */}
      <section className="hero">
        <div className="hero-bg-orbs">
          <div className="orb"></div><div className="orb"></div><div className="orb"></div>
        </div>
        <div className="hero-content">
          <div className="hero-badge"><span className="dot"></span> AR-Powered Shopping Experience</div>
          <h1>See Products in <span className="gradient-text">Augmented Reality</span> Before You Buy</h1>
          <p>Scan, explore 3D models, read reviews, and place products in your space — all from your browser. No app required.</p>
          <div className="hero-actions">
            <Link to="/catalog" className="btn btn-primary">🛍️ Browse Products</Link>
            <Link to="/scanner" className="btn btn-secondary">📷 Scan QR Code</Link>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="section" id="how-it-works">
        <div className="section-header">
          <span className="tag">How It Works</span>
          <h2>Four Simple Steps</h2>
          <p>Our AR system makes product exploration effortless and immersive.</p>
        </div>
        <div className="steps-grid">
          <div className="glass-card step-card">
            <div className="step-num">1</div>
            <div className="step-icon">📱</div>
            <h3>Scan QR Code</h3>
            <p>Point your camera at any product QR code to instantly access its AR page.</p>
          </div>
          <div className="glass-card step-card">
            <div className="step-num">2</div>
            <div className="step-icon">🧊</div>
            <h3>View 3D Model</h3>
            <p>Interact with a detailed 3D model — rotate, zoom, and inspect every angle.</p>
          </div>
          <div className="glass-card step-card">
            <div className="step-num">3</div>
            <div className="step-icon">⭐</div>
            <h3>Read AR Reviews</h3>
            <p>See ratings and customer reviews overlaid right alongside the product.</p>
          </div>
          <div className="glass-card step-card">
            <div className="step-num">4</div>
            <div className="step-icon">🛒</div>
            <h3>Buy with Confidence</h3>
            <p>Make informed purchase decisions with full product visualization and trust.</p>
          </div>
        </div>
      </section>

      {/* FEATURED PRODUCTS */}
      <section className="section" id="featured">
        <div className="section-header">
          <span className="tag">Featured</span>
          <h2>Explore in AR</h2>
          <p>Our top-rated products with interactive 3D models and real customer reviews.</p>
        </div>
        <div className="products-grid">
          {featured.map(product => <ProductCard key={product.id} product={product} />)}
        </div>
        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <Link to="/catalog" className="btn btn-secondary">View All Products →</Link>
        </div>
      </section>
    </>
  );
}

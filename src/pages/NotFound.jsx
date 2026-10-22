import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="section" style={{ textAlign: 'center', minHeight: '70vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <p style={{ fontSize: '6rem', marginBottom: '0.5rem', lineHeight: 1 }}>🔭</p>
      <h1 style={{ fontSize: '4rem', fontWeight: 900, marginBottom: '1rem' }}>
        <span className="gradient-text">404</span>
      </h1>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1rem' }}>Page Not Found</h2>
      <p style={{ color: 'var(--text-secondary)', maxWidth: '400px', marginBottom: '2rem' }}>
        The page you're looking for doesn't exist or has been moved. Let's get you back on track.
      </p>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
        <Link to="/" className="btn btn-primary">🏠 Go Home</Link>
        <Link to="/catalog" className="btn btn-secondary">🛍️ Browse Products</Link>
      </div>
    </div>
  );
}

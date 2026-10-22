import { useState, Suspense } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stage, useGLTF, Html } from '@react-three/drei';
import '@google/model-viewer';
import { PRODUCTS } from '../data';
import { useReviews } from '../hooks/useReviews';
import StarRating from '../components/StarRating';

function Model({ url, wireframe }) {
  const { scene } = useGLTF(url);
  
  // Apply wireframe to all materials if needed
  scene.traverse((child) => {
    if (child.isMesh && child.material) {
      child.material.wireframe = wireframe;
    }
  });

  return <primitive object={scene} />;
}


export default function ProductDetail() {
  const [searchParams] = useSearchParams();
  const productId = searchParams.get('id');
  const product = PRODUCTS.find(p => p.id === productId);
  
  const { reviews, addReview, getAverageRating } = useReviews(productId);
  const avgRating = getAverageRating(product?.rating);

  const [autoRotate, setAutoRotate] = useState(true);
  const [wireframe, setWireframe] = useState(false);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewName, setReviewName] = useState('');
  const [reviewText, setReviewText] = useState('');
  const [selectedRating, setSelectedRating] = useState(0);
  const [toast, setToast] = useState('');

  if (!product) {
    return (
      <div className="section" style={{textAlign: 'center', padding: '4rem'}}>
        <p style={{fontSize: '4rem'}}>❌</p>
        <h2 style={{margin: '1rem 0'}}>Product Not Found</h2>
        <p style={{color: 'var(--text-secondary)', marginBottom: '1.5rem'}}>The product you're looking for doesn't exist.</p>
        <Link to="/catalog" className="btn btn-primary">Browse Products</Link>
      </div>
    );
  }

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  };

  const handleSubmitReview = () => {
    if (!reviewName || !reviewText || !selectedRating) {
      showToast('⚠️ Please fill in all fields and select a rating.');
      return;
    }
    addReview({
      user: reviewName,
      rating: selectedRating,
      date: new Date().toISOString().split('T')[0],
      text: reviewText
    });
    setReviewName('');
    setReviewText('');
    setSelectedRating(0);
    setShowReviewForm(false);
    showToast('✅ Review submitted successfully!');
  };

  return (
    <div className="section product-detail">
      <Link to="/catalog" className="btn btn-secondary btn-sm" style={{marginBottom: '1.5rem'}}>← Back to Catalog</Link>
      
      <div className="product-layout">
        {/* 3D Viewer & AR */}
        <div>
          <div className="viewer-container">
            <Canvas shadows camera={{ position: [0, 1.5, 3], fov: 45 }}>
              <color attach="background" args={['#0a0a0f']} />
              <ambientLight intensity={0.6} />
              <directionalLight position={[5, 8, 5]} intensity={1.5} castShadow />
              <directionalLight position={[-5, 3, -5]} intensity={0.3} color="#00d4ff" />
              <Suspense fallback={
                <Html center>
                  <div className="viewer-loading">
                    <div className="spinner"></div>
                    <span>Loading Model...</span>
                  </div>
                </Html>
              }>
                <Stage environment="city" intensity={0.5} contactShadow={{ resolution: 1024, scale: 10 }}>
                  <Model url={product.modelSrc} wireframe={wireframe} />
                </Stage>
              </Suspense>
              <OrbitControls 
                autoRotate={autoRotate}
                autoRotateSpeed={2}
                enableDamping
                dampingFactor={0.05}
                minDistance={1}
                maxDistance={8}
              />
            </Canvas>
            
            <div className="viewer-controls">
              <button className={autoRotate ? 'active' : ''} onClick={() => setAutoRotate(!autoRotate)}>🔄 Rotate</button>
              <button className={wireframe ? 'active' : ''} onClick={() => setWireframe(!wireframe)}>🔲 Wire</button>
            </div>
            <div style={{position: 'absolute', top: '1rem', left: '1rem', padding: '0.3rem 0.8rem', borderRadius: 'var(--radius-sm)', background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(10px)', fontSize: '0.75rem', color: 'var(--accent-cyan)'}}>
              🖱️ Drag to rotate · Scroll to zoom
            </div>
          </div>

          <div className="ar-button-wrap">
            <h3 style={{marginBottom: '0.8rem', fontSize: '1rem'}}>📱 View in Your Space (AR)</h3>
            <model-viewer
              src={product.modelSrc}
              ar
              ar-modes="webxr scene-viewer quick-look"
              camera-controls
              touch-action="pan-y"
              shadow-intensity="1"
              auto-rotate
              style={{width: '100%', height: '350px', borderRadius: 'var(--radius-lg)', background: 'var(--bg-card)'}}
            >
              <button slot="ar-button" style={{position: 'absolute', bottom: '1rem', left: '50%', transform: 'translateX(-50%)', padding: '0.6rem 1.5rem', borderRadius: 'var(--radius-xl)', background: 'var(--accent-cyan)', color: '#000', fontWeight: '700', border: 'none', fontSize: '0.9rem', cursor: 'pointer'}}>
                🔮 View in AR
              </button>
              <div slot="hotspot-rating" className="ar-hotspot" data-position="0 0.5 0" data-normal="0 1 0" style={{maxWidth: '250px', textAlign: 'left'}}>
                <div className="hotspot-content">
                  <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem'}}>
                    <span style={{fontSize: '1.2rem', fontWeight: '900', color: '#ffc107'}}>⭐ {avgRating}</span>
                    <span style={{fontSize: '0.8rem', color: 'var(--text-secondary)'}}>({reviews.length || product.reviewCount} reviews)</span>
                  </div>
                  {reviews.length > 0 && (
                    <div style={{fontSize: '0.85rem', color: '#fff', borderTop: '1px solid rgba(255,255,255,0.2)', paddingTop: '0.5rem', marginTop: '0.5rem'}}>
                      <strong>{reviews[0].user}:</strong> "{reviews[0].text.length > 60 ? reviews[0].text.substring(0, 60) + '...' : reviews[0].text}"
                    </div>
                  )}
                </div>
              </div>
            </model-viewer>
          </div>
        </div>

        {/* Product Info */}
        <div className="product-meta">
          <div className="meta-category">{product.category}</div>
          <h1>{product.name}</h1>
          <div style={{display: 'flex', alignItems: 'center', gap: '1rem', margin: '0.5rem 0'}}>
            <StarRating rating={avgRating} readOnly />
            <span style={{fontSize: '1.1rem', fontWeight: '700'}}>{avgRating}</span>
            <span style={{color: 'var(--text-secondary)', fontSize: '0.9rem'}}>({reviews.length || product.reviewCount} reviews)</span>
          </div>
          <div className="meta-price">${product.price.toFixed(2)}</div>
          <p className="meta-desc">{product.description}</p>

          <h3 style={{fontSize: '1rem', marginBottom: '0.5rem'}}>Specifications</h3>
          <table className="specs-table">
            <tbody>
              {Object.entries(product.specs).map(([k, v]) => (
                <tr key={k}>
                  <td>{k}</td>
                  <td style={{fontWeight: '600'}}>{v}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* QR Code */}
          <div className="glass-card qr-section">
            <h3>📱 Share via QR Code</h3>
            <p style={{color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem'}}>Scan this QR code to view this product on any device.</p>
            <div style={{display: 'flex', justifyContent: 'center', padding: '1rem', background: '#fff', borderRadius: 'var(--radius-md)', width: 'fit-content', margin: '0 auto'}}>
              <QRCodeSVG value={typeof window !== 'undefined' ? window.location.href : ''} size={150} />
            </div>
          </div>
        </div>
      </div>

      {/* Reviews */}
      <div className="reviews-section">
        <div className="reviews-header">
          <div>
            <h2 style={{fontSize: '1.5rem'}}>Customer Reviews</h2>
            <div className="reviews-summary" style={{marginTop: '0.5rem'}}>
              <span className="big-rating">{avgRating}</span>
              <div>
                <StarRating rating={avgRating} readOnly />
                <span style={{color: 'var(--text-secondary)', fontSize: '0.85rem'}}>{reviews.length || product.reviewCount} reviews</span>
              </div>
            </div>
          </div>
          <button className="btn btn-primary" onClick={() => setShowReviewForm(!showReviewForm)}>✍️ Write a Review</button>
        </div>

        {showReviewForm && (
          <div className="glass-card review-form">
            <h3>Write Your Review</h3>
            <div className="form-group">
              <label>Your Name</label>
              <input type="text" value={reviewName} onChange={e => setReviewName(e.target.value)} placeholder="Enter your name" />
            </div>
            <div className="form-group">
              <label>Rating</label>
              <StarRating rating={selectedRating} onChange={setSelectedRating} />
            </div>
            <div className="form-group">
              <label>Your Review</label>
              <textarea value={reviewText} onChange={e => setReviewText(e.target.value)} placeholder="Share your experience..."></textarea>
            </div>
            <button className="btn btn-primary" onClick={handleSubmitReview}>Submit Review</button>
          </div>
        )}

        <div>
          {reviews.length === 0 ? (
            <p style={{color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem'}}>No reviews yet. Be the first to review!</p>
          ) : (
            reviews.map((r, i) => (
              <div key={i} className="glass-card review-card">
                <div className="review-header">
                  <span className="reviewer">👤 {r.user}</span>
                  <span className="review-date">{r.date}</span>
                </div>
                <StarRating rating={r.rating} readOnly />
                <p className="review-text">{r.text}</p>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Toast Notification */}
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

# Project Documentation

## Source Code

### src/App.css

```css
/* App-level styles - all main styles live in index.css */

```

### src/App.jsx

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ScrollToTop from './components/ScrollToTop';
import Home from './pages/Home';
import Catalog from './pages/Catalog';
import ProductDetail from './pages/ProductDetail';
import Scanner from './pages/Scanner';
import NotFound from './pages/NotFound';

function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/catalog" element={<Catalog />} />
        <Route path="/product" element={<ProductDetail />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  );
}

export default App;

```

### src/components/Footer.jsx

```jsx
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

```

### src/components/Navbar.jsx

```jsx
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

```

### src/components/ProductCard.jsx

```jsx
import { Link } from 'react-router-dom';
import StarRating from './StarRating';
import { useReviews } from '../hooks/useReviews';

export default function ProductCard({ product }) {
  const { getAverageRating, reviews } = useReviews(product.id);
  const avgRating = getAverageRating(product.rating);

  return (
    <Link to={`/product?id=${product.id}`} className="glass-card product-card">
      <div className="product-img">
        <span>{product.emoji}</span>
        <span className="ar-badge">AR Ready</span>
      </div>
      <div className="product-info">
        <div className="product-category">{product.category}</div>
        <div className="product-name">{product.name}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <StarRating rating={avgRating} readOnly />
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            ({reviews.length || product.reviewCount})
          </span>
        </div>
        <div className="product-price">${product.price.toFixed(2)}</div>
      </div>
    </Link>
  );
}

```

### src/components/ScrollToTop.jsx

```jsx
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export default function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [pathname]);

  return null;
}

```

### src/components/StarRating.jsx

```jsx
import { useState } from 'react';

export default function StarRating({ rating, readOnly = false, onChange = () => {} }) {
  const [hover, setHover] = useState(0);

  return (
    <div className={`stars ${!readOnly ? 'star-input' : ''}`}>
      {[1, 2, 3, 4, 5].map((star) => (
        <span
          key={star}
          className={`star ${star <= (hover || rating) ? 'filled active' : ''}`}
          style={{ 
            color: star <= (hover || Math.round(rating)) ? '#ffc107' : 'var(--text-muted)',
            cursor: readOnly ? 'default' : 'pointer'
          }}
          onClick={() => !readOnly && onChange(star)}
          onMouseEnter={() => !readOnly && setHover(star)}
          onMouseLeave={() => !readOnly && setHover(0)}
        >
          ★
        </span>
      ))}
    </div>
  );
}

```

### src/data.js

```js
export const PRODUCTS = [
  {
    id: 'astronaut',
    name: 'Astronaut Helmet',
    category: 'Accessories',
    price: 299.99,
    rating: 4.7,
    reviewCount: 124,
    emoji: '🧑‍🚀',
    description: 'A detailed replica astronaut helmet perfect for display or cosplay. Features realistic visor reflection coating and adjustable interior padding.',
    specs: { 'Material': 'ABS Plastic + Polycarbonate', 'Weight': '1.2 kg', 'Dimensions': '30 × 28 × 35 cm', 'Color': 'White / Gold Visor', 'Warranty': '1 Year' },
    modelSrc: 'https://modelviewer.dev/shared-assets/models/glTF-Sample-Assets/Models/DamagedHelmet/glTF-Binary/DamagedHelmet.glb',
    iosSrc: '',
    image: 'https://modelviewer.dev/shared-assets/models/glTF-Sample-Assets/Models/DamagedHelmet/screenshot/screenshot-large.jpg'
  },
  {
    id: 'robot',
    name: 'Robot Companion',
    category: 'Electronics',
    price: 599.99,
    rating: 4.9,
    reviewCount: 287,
    emoji: '🤖',
    description: 'An AI-powered desktop robot companion with expressive movements and voice interaction. Responds to gestures and provides ambient lighting.',
    specs: { 'Connectivity': 'WiFi + Bluetooth 5.0', 'Battery': '4000mAh (8hr)', 'Sensors': 'Camera, Mic, ToF', 'Height': '22 cm', 'Warranty': '2 Years' },
    modelSrc: 'https://modelviewer.dev/shared-assets/models/RobotExpressive.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'horse',
    name: 'Decorative Horse Sculpture',
    category: 'Home Décor',
    price: 149.99,
    rating: 4.5,
    reviewCount: 89,
    emoji: '🐴',
    description: 'A stunning hand-crafted horse sculpture with metallic finish. An elegant centerpiece for any living room or office space.',
    specs: { 'Material': 'Resin + Metal Coating', 'Weight': '2.5 kg', 'Dimensions': '35 × 10 × 30 cm', 'Finish': 'Brushed Bronze', 'Warranty': '6 Months' },
    modelSrc: 'https://modelviewer.dev/shared-assets/models/Horse.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'chair',
    name: 'Sheen Office Chair',
    category: 'Furniture',
    price: 449.99,
    rating: 4.6,
    reviewCount: 203,
    emoji: '🪑',
    description: 'Ergonomic mesh office chair with lumbar support, adjustable armrests, and breathable fabric. Designed for all-day comfort during work.',
    specs: { 'Material': 'Mesh + Steel Frame', 'Max Weight': '120 kg', 'Adjustable Height': '42–52 cm', 'Armrests': 'Adjustable', 'Warranty': '5 Years' },
    modelSrc: 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/SheenChair/glTF-Binary/SheenChair.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'boom-box',
    name: 'Retro Boom Box Speaker',
    category: 'Electronics',
    price: 179.99,
    rating: 4.8,
    reviewCount: 342,
    emoji: '📻',
    description: 'Vintage-styled bluetooth speaker with modern audio tech. Delivers rich bass and 360° surround sound with a nostalgic retro aesthetic.',
    specs: { 'Output': '40W Stereo', 'Battery': '6000mAh (12hr)', 'Connectivity': 'BT 5.2 + AUX', 'Weight': '3.2 kg', 'Warranty': '2 Years' },
    modelSrc: 'https://modelviewer.dev/shared-assets/models/glTF-Sample-Assets/Models/BoomBox/glTF-Binary/BoomBox.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'lantern',
    name: 'Smart Ambient Lantern',
    category: 'Home Décor',
    price: 79.99,
    rating: 4.4,
    reviewCount: 156,
    emoji: '🏮',
    description: 'WiFi-enabled smart lantern with adjustable color temperature and brightness. Create the perfect ambiance with app-controlled lighting.',
    specs: { 'Lumens': '800 lm', 'Color Temp': '2700K–6500K', 'Control': 'App / Voice', 'Battery': '3000mAh', 'Warranty': '1 Year' },
    modelSrc: 'https://modelviewer.dev/shared-assets/models/glTF-Sample-Assets/Models/Lantern/glTF-Binary/Lantern.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'sofa',
    name: 'Cloud Comfort Sofa',
    category: 'Furniture',
    price: 1299.99,
    rating: 4.3,
    reviewCount: 67,
    emoji: '🛋️',
    description: 'Ultra-soft 3-seater sofa with memory foam cushions and stain-resistant fabric. Modular design allows flexible living room configurations.',
    specs: { 'Seating': '3-Seater', 'Material': 'Linen + Memory Foam', 'Dimensions': '210 × 90 × 85 cm', 'Weight': '45 kg', 'Warranty': '3 Years' },
    modelSrc: 'https://arlo.tools/models/sofa.glb',
    iosSrc: '',
    image: ''
  },
  {
    id: 'headphones',
    name: 'ProSound ANC Headphones',
    category: 'Electronics',
    price: 349.99,
    rating: 4.8,
    reviewCount: 521,
    emoji: '🎧',
    description: 'Premium noise-cancelling headphones with spatial audio support. 40mm drivers deliver studio-quality sound with 30-hour battery life.',
    specs: { 'Driver': '40mm Dynamic', 'ANC': 'Hybrid Active', 'Battery': '30 Hours', 'Connectivity': 'BT 5.3 + USB-C', 'Warranty': '2 Years' },
    modelSrc: 'https://arlo.tools/models/Headphones.glb',
    iosSrc: '',
    image: ''
  }
];

export const REVIEWS_DATA = {
  'astronaut': [
    { user: 'SpaceFan42', rating: 5, date: '2026-06-15', text: 'Incredible detail! The visor coating looks amazing and the build quality is top-notch.' },
    { user: 'CosplayKing', rating: 4, date: '2026-06-10', text: 'Great for my costume collection. Slightly heavy but very comfortable to wear.' },
    { user: 'NASANerd', rating: 5, date: '2026-05-28', text: 'Best replica I have found at this price. The AR preview matched perfectly with what I received.' }
  ],
  'robot': [
    { user: 'TechLover99', rating: 5, date: '2026-06-20', text: 'This little robot has become my desk buddy. The AI responses are surprisingly smart!' },
    { user: 'GadgetGuru', rating: 5, date: '2026-06-12', text: 'Absolutely love the expressive movements. Kids are obsessed with it too.' },
    { user: 'MinimalDesk', rating: 4, date: '2026-06-01', text: 'Great design and functionality. Wish the battery lasted a bit longer.' }
  ],
  'horse': [
    { user: 'ArtCollector', rating: 5, date: '2026-06-18', text: 'Stunning piece. The bronze finish catches light beautifully. A real conversation starter.' },
    { user: 'HomeDesigner', rating: 4, date: '2026-06-05', text: 'Elegant and well-crafted. Slightly smaller than I expected but still gorgeous.' }
  ],
  'chair': [
    { user: 'RemoteWorker', rating: 5, date: '2026-06-22', text: 'Best office chair I have owned. My back pain is gone after switching to this.' },
    { user: 'GamerPro', rating: 4, date: '2026-06-14', text: 'Very comfortable for long gaming sessions. The mesh keeps you cool.' },
    { user: 'OfficeManager', rating: 5, date: '2026-05-30', text: 'Ordered 20 of these for our office. Everyone loves them.' }
  ],
  'boom-box': [
    { user: 'MusicHead', rating: 5, date: '2026-06-21', text: 'The sound quality is insane for a portable speaker. Bass hits hard!' },
    { user: 'RetroLover', rating: 5, date: '2026-06-16', text: 'Love the vintage look with modern tech inside. Turns heads everywhere.' },
    { user: 'PartyDJ', rating: 4, date: '2026-06-08', text: 'Great speaker for outdoor parties. Battery life is impressive.' }
  ],
  'lantern': [
    { user: 'CozyHome', rating: 4, date: '2026-06-19', text: 'Creates beautiful ambient light. The app control is convenient.' },
    { user: 'SmartHomeFan', rating: 5, date: '2026-06-11', text: 'Integrates perfectly with my smart home setup. Love the color options.' }
  ],
  'sofa': [
    { user: 'LivingRoomLove', rating: 4, date: '2026-06-17', text: 'Super comfortable and stylish. Delivery and setup were smooth.' },
    { user: 'FamilyOf4', rating: 5, date: '2026-06-09', text: 'Our whole family fits comfortably. The stain-resistant fabric is a lifesaver with kids.' }
  ],
  'headphones': [
    { user: 'Audiophile', rating: 5, date: '2026-06-23', text: 'Studio-quality sound with incredible noise cancellation. Worth every penny.' },
    { user: 'Commuter', rating: 5, date: '2026-06-15', text: 'Perfect for my daily commute. The ANC blocks out all subway noise.' },
    { user: 'PodcastFan', rating: 4, date: '2026-06-07', text: 'Crystal clear voice quality. Battery easily lasts my whole work week.' }
  ]
};

export const CATEGORIES = ['All', 'Electronics', 'Furniture', 'Home Décor', 'Accessories'];

export function getProduct(id) {
  return PRODUCTS.find(p => p.id === id);
}

```

### src/hooks/useReviews.js

```js
import { useState, useEffect } from 'react';
import { REVIEWS_DATA } from '../data';

export function useReviews(productId) {
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    if (!productId) return;
    const stored = localStorage.getItem(`reviews_${productId}`);
    const base = REVIEWS_DATA[productId] || [];
    setReviews(stored ? [...base, ...JSON.parse(stored)] : [...base]);
  }, [productId]);

  const addReview = (review) => {
    const newReviews = [...reviews, review];
    const stored = JSON.parse(localStorage.getItem(`reviews_${productId}`) || '[]');
    stored.push(review);
    localStorage.setItem(`reviews_${productId}`, JSON.stringify(stored));
    setReviews(newReviews);
  };

  const getAverageRating = (defaultRating) => {
    if (reviews.length === 0) return defaultRating;
    const sum = reviews.reduce((acc, r) => acc + r.rating, 0);
    return Number((sum / reviews.length).toFixed(1));
  };

  return { reviews, addReview, getAverageRating };
}

```

### src/index.css

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
  --font: 'Inter', sans-serif;
  --bg-main: #0a0a0f;
  --bg-card: rgba(25, 25, 35, 0.6);
  --accent-cyan: #00d4ff;
  --accent-purple: #8a2be2;
  --gradient-main: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
  --text-primary: #ffffff;
  --text-secondary: #a0a0b0;
  --text-muted: #555565;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --radius-xl: 30px;
  --shadow-card: 0 10px 30px rgba(0, 0, 0, 0.5);
  --shadow-glow: 0 0 20px rgba(0, 212, 255, 0.3);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: var(--font);
  background-color: var(--bg-main);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  overflow-x: hidden;
}

a {
  text-decoration: none;
  color: inherit;
}

/* ========= Page Transition ========= */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.section {
  animation: fadeInUp 0.5s ease-out;
}

/* ========= Glassmorphism Utilities ========= */
.glass-card {
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

/* ========= Buttons ========= */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0.8rem 1.8rem;
  border-radius: var(--radius-xl);
  font-family: var(--font);
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  text-align: center;
}
.btn-primary {
  background: var(--gradient-main);
  color: #fff;
  box-shadow: var(--shadow-glow);
}
.btn-primary:hover {
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
  transform: translateY(-2px);
}
.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}
.btn-sm {
  padding: 0.5rem 1.2rem;
  font-size: 0.9rem;
}

/* ========= Navbar ========= */
.navbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 5%;
  z-index: 1000;
  transition: all 0.3s ease;
}
.navbar.scrolled {
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.4rem;
  font-weight: 800;
  letter-spacing: -0.5px;
}
.brand-icon {
  background: var(--gradient-main);
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.nav-links {
  display: flex;
  gap: 2rem;
  align-items: center;
}
.nav-links a {
  font-weight: 600;
  color: var(--text-secondary);
  transition: color 0.2s;
  position: relative;
}
.nav-links a:hover, .nav-links a.active {
  color: #fff;
}
.nav-links a.active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background: var(--gradient-main);
  border-radius: 3px;
}
.nav-cta {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1.2rem;
  border-radius: var(--radius-xl);
  color: #fff !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
.nav-cta::after { display: none !important; }
.nav-cta:hover { background: rgba(255, 255, 255, 0.2); }
.nav-toggle { display: none; background: transparent; border: none; cursor: pointer; flex-direction: column; gap: 5px; }
.nav-toggle span { width: 25px; height: 3px; background: #fff; border-radius: 2px; transition: 0.3s; }

/* ========= Sections ========= */
.section { padding: 100px 5% 50px; max-width: 1400px; margin: 0 auto; }
.section-header { text-align: center; margin-bottom: 3rem; }
.section-header .tag {
  display: inline-block;
  padding: 0.4rem 1rem;
  border-radius: var(--radius-xl);
  background: rgba(0, 212, 255, 0.1);
  color: var(--accent-cyan);
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 1rem;
}
.section-header h2 { font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem; }
.section-header p { color: var(--text-secondary); max-width: 600px; margin: 0 auto; font-size: 1.1rem; }

/* ========= Hero ========= */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding-top: 70px;
}
.hero-content {
  text-align: center;
  max-width: 800px;
  z-index: 2;
  padding: 0 5%;
  animation: fadeInUp 0.8s ease-out;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0.5rem 1rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: var(--radius-xl);
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 2rem;
}
.hero-badge .dot {
  width: 8px; height: 8px;
  background: #00ff88;
  border-radius: 50%;
  box-shadow: 0 0 10px #00ff88;
  animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; box-shadow: 0 0 10px #00ff88; }
  50% { opacity: 0.6; box-shadow: 0 0 20px #00ff88; }
}
.hero h1 {
  font-size: 4.5rem;
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  letter-spacing: -1.5px;
}
.gradient-text {
  background: var(--gradient-main);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero p {
  font-size: 1.2rem;
  color: var(--text-secondary);
  margin-bottom: 2.5rem;
  max-width: 600px;
  margin-inline: auto;
}
.hero-actions { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
.hero-bg-orbs {
  position: absolute; top: 0; left: 0;
  width: 100%; height: 100%;
  z-index: 1; pointer-events: none;
}
.orb { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.4; }
.orb:nth-child(1) { width: 400px; height: 400px; background: var(--accent-cyan); top: -100px; left: -100px; animation: float 10s infinite alternate; }
.orb:nth-child(2) { width: 500px; height: 500px; background: var(--accent-purple); bottom: -200px; right: -100px; animation: float 12s infinite alternate-reverse; }
.orb:nth-child(3) { width: 300px; height: 300px; background: #ff6b9d; top: 50%; right: 20%; animation: float 14s infinite alternate; opacity: 0.2; }
@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(50px, 50px) scale(1.1); }
}

/* ========= Grid Layouts ========= */
.steps-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; }
.step-card {
  padding: 2.5rem 2rem;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.step-card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 212, 255, 0.2);
}
.step-num {
  position: absolute; top: -20px; right: -10px;
  font-size: 8rem; font-weight: 900;
  color: rgba(255,255,255,0.03); line-height: 1;
}
.step-icon { font-size: 3rem; margin-bottom: 1.5rem; }
.step-card h3 { margin-bottom: 1rem; font-size: 1.3rem; }
.step-card p { color: var(--text-secondary); font-size: 0.95rem; }

.products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; }
.product-card { display: flex; flex-direction: column; overflow: hidden; cursor: pointer; }
.product-card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 15px 35px rgba(0,0,0,0.6), 0 0 15px rgba(0, 212, 255, 0.15);
}
.product-img {
  height: 220px;
  background: rgba(0,0,0,0.3);
  display: flex; align-items: center; justify-content: center;
  font-size: 5rem; position: relative;
  overflow: hidden;
}
.product-img::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 60px;
  background: linear-gradient(to top, var(--bg-card), transparent);
  pointer-events: none;
}
.ar-badge {
  position: absolute; top: 1rem; right: 1rem;
  background: rgba(0, 212, 255, 0.2);
  border: 1px solid var(--accent-cyan);
  color: var(--accent-cyan);
  padding: 0.3rem 0.8rem;
  border-radius: var(--radius-xl);
  font-size: 0.75rem; font-weight: 700;
  backdrop-filter: blur(4px);
  z-index: 2;
}
.product-info {
  padding: 1.5rem;
  display: flex; flex-direction: column; gap: 0.5rem;
}
.product-category { color: var(--accent-cyan); font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.product-name { font-size: 1.25rem; font-weight: 700; }
.product-price { font-size: 1.4rem; font-weight: 900; margin-top: 0.5rem; }

/* ========= Stars ========= */
.stars { display: inline-flex; gap: 2px; }
.star { font-size: 1.2rem; transition: color 0.2s, transform 0.2s; }
.star-input .star:hover { transform: scale(1.2); }

/* ========= Catalog Page ========= */
.catalog-layout { display: grid; grid-template-columns: 280px 1fr; gap: 3rem; align-items: start; }
.filters-panel { padding: 1.5rem; position: sticky; top: 100px; }
.search-wrap { position: relative; margin-bottom: 2rem; }
.search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--text-secondary); }
.search-box {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 2.8rem;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: var(--radius-md);
  color: #fff;
  font-family: var(--font);
  font-size: 0.95rem;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.search-box:focus {
  outline: none;
  border-color: var(--accent-cyan);
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.15);
}
.filter-group { margin-bottom: 2rem; }
.filter-group h4 { margin-bottom: 1rem; font-size: 0.95rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }
.filter-btn {
  display: block; width: 100%; text-align: left;
  padding: 0.8rem 1rem; background: transparent;
  border: none; color: var(--text-primary);
  font-family: var(--font); font-size: 1rem; font-weight: 500;
  cursor: pointer; border-radius: var(--radius-sm);
  transition: 0.2s; margin-bottom: 0.3rem;
}
.filter-btn:hover { background: rgba(255,255,255,0.05); }
.filter-btn.active { background: rgba(0, 212, 255, 0.1); color: var(--accent-cyan); font-weight: 700; }
.sort-select {
  width: 100%; padding: 0.8rem;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: var(--radius-md);
  color: #fff;
  font-family: var(--font); font-size: 0.95rem;
  cursor: pointer;
}
.catalog-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.results-count { color: var(--text-secondary); font-weight: 500; }

/* ========= Product Detail ========= */
.product-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; margin-bottom: 4rem; }
.viewer-container {
  width: 100%; height: 500px;
  background: rgba(0,0,0,0.4);
  border-radius: var(--radius-lg);
  overflow: hidden; position: relative;
  border: 1px solid rgba(255,255,255,0.05);
}
.viewer-controls {
  position: absolute; bottom: 1.5rem; left: 50%; transform: translateX(-50%);
  display: flex; gap: 0.5rem;
  background: rgba(10,10,15,0.8);
  padding: 0.5rem; border-radius: var(--radius-xl);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.1);
}
.viewer-controls button {
  background: transparent; border: none;
  color: #fff; padding: 0.5rem 1rem;
  border-radius: var(--radius-xl); cursor: pointer;
  font-family: var(--font); font-weight: 600;
  transition: 0.2s;
}
.viewer-controls button:hover { background: rgba(255,255,255,0.1); }
.viewer-controls button.active { background: var(--accent-cyan); color: #000; }
.ar-button-wrap { margin-top: 1.5rem; position: relative; }
.ar-hotspot {
  display: block; width: fit-content;
  padding: 0.8rem 1rem;
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  pointer-events: none;
}
.product-meta h1 { font-size: 2.5rem; font-weight: 900; line-height: 1.1; margin-bottom: 1rem; }
.meta-category { color: var(--accent-cyan); font-weight: 700; text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem; }
.meta-price { font-size: 2.2rem; font-weight: 900; color: #fff; margin: 1.5rem 0; }
.meta-desc { color: var(--text-secondary); font-size: 1.1rem; margin-bottom: 2rem; line-height: 1.7; }
.specs-table { width: 100%; border-collapse: collapse; margin-bottom: 2rem; }
.specs-table td { padding: 1rem 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
.specs-table td:first-child { color: var(--text-secondary); width: 40%; }
.qr-section { padding: 1.5rem; text-align: center; }

/* 3D Viewer Loading Spinner */
.viewer-loading {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  display: flex; flex-direction: column;
  align-items: center; gap: 1rem;
  z-index: 5;
}
.spinner {
  width: 40px; height: 40px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: var(--accent-cyan);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.viewer-loading span {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 600;
}

/* ========= Reviews ========= */
.reviews-section { max-width: 800px; margin: 0 auto; }
.reviews-header {
  display: flex; justify-content: space-between; align-items: flex-end;
  margin-bottom: 2rem; padding-bottom: 2rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.reviews-summary { display: flex; align-items: center; gap: 1rem; }
.big-rating { font-size: 3rem; font-weight: 900; line-height: 1; }
.review-form { padding: 2rem; margin-bottom: 2rem; }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
.form-group input, .form-group textarea {
  width: 100%; padding: 1rem;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: var(--radius-md);
  color: #fff;
  font-family: var(--font); font-size: 1rem;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.form-group input:focus, .form-group textarea:focus {
  outline: none;
  border-color: var(--accent-cyan);
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.15);
}
.form-group textarea { min-height: 120px; resize: vertical; }
.review-card { padding: 1.5rem; margin-bottom: 1rem; }
.review-card:hover { border-color: rgba(255, 255, 255, 0.1); }
.review-header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.reviewer { font-weight: 700; }
.review-date { color: var(--text-secondary); font-size: 0.85rem; }
.review-text { margin-top: 1rem; color: #ddd; line-height: 1.6; }

/* ========= Scanner ========= */
.scanner-page { max-width: 600px; margin: 0 auto; text-align: center; }
.scan-item {
  display: flex; justify-content: space-between;
  padding: 1rem 1.5rem; margin-bottom: 0.5rem; text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease;
}
.scan-item:hover { border-color: rgba(0, 212, 255, 0.2); }
.scan-time { color: var(--text-secondary); font-size: 0.85rem; }
.scan-history h3 { margin-bottom: 1rem; }

/* ========= Footer ========= */
.footer {
  background: rgba(10,10,15,0.9);
  border-top: 1px solid rgba(255,255,255,0.05);
  padding: 80px 5% 40px;
  margin-top: 100px;
}
.footer-content {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 4rem;
  max-width: 1400px;
  margin: 0 auto;
  margin-bottom: 4rem;
}
.footer-brand p { color: var(--text-secondary); margin-top: 1rem; font-size: 0.95rem; }
.footer-col h4 { margin-bottom: 1.5rem; font-size: 1.1rem; }
.footer-col a { display: block; color: var(--text-secondary); margin-bottom: 0.8rem; transition: color 0.2s; }
.footer-col a:hover { color: var(--accent-cyan); }
.footer-bottom {
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(255,255,255,0.05);
}

/* ========= Toast Notification ========= */
.toast {
  position: fixed;
  bottom: 2rem; right: 2rem;
  background: rgba(25, 25, 35, 0.95);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: var(--radius-md);
  padding: 1rem 1.5rem;
  color: #fff;
  font-weight: 600;
  z-index: 9999;
  animation: slideInRight 0.4s ease-out;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 212, 255, 0.15);
}
@keyframes slideInRight {
  from { opacity: 0; transform: translateX(40px); }
  to { opacity: 1; transform: translateX(0); }
}

/* ========= Custom Scrollbar ========= */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--bg-main); }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.25); }

/* ========= Selection ========= */
::selection {
  background: rgba(0, 212, 255, 0.3);
  color: #fff;
}

/* ========= Responsive ========= */
@media (max-width: 900px) {
  .product-layout, .catalog-layout, .footer-content {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  .hero h1 { font-size: 2.8rem; }
  .navbar { padding: 0 1rem; }
  .nav-links {
    display: none;
    position: absolute;
    top: 70px; left: 0;
    width: 100%;
    background: rgba(10,10,15,0.95);
    backdrop-filter: blur(15px);
    flex-direction: column;
    padding: 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
  .nav-links.open { display: flex; }
  .nav-toggle { display: flex; }
  .hero-actions { flex-direction: column; align-items: center; }
  .section-header h2 { font-size: 2rem; }
  .product-meta h1 { font-size: 1.8rem; }
  .meta-price { font-size: 1.6rem; }
  .reviews-header { flex-direction: column; align-items: flex-start; gap: 1rem; }
  .filters-panel { position: static; }
}

@media (max-width: 480px) {
  .hero h1 { font-size: 2.2rem; }
  .section { padding: 80px 4% 30px; }
  .products-grid { grid-template-columns: 1fr; }
  .steps-grid { grid-template-columns: 1fr; }
}

```

### src/main.jsx

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

```

### src/pages/Catalog.jsx

```jsx
import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PRODUCTS, CATEGORIES } from '../data';
import ProductCard from '../components/ProductCard';
import { Search } from 'lucide-react';

export default function Catalog() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeCategory = searchParams.get('cat') || 'All';
  const [query, setQuery] = useState('');
  const [sort, setSort] = useState('rating');

  const filtered = PRODUCTS.filter(p => {
    const matchCat = activeCategory === 'All' || p.category === activeCategory;
    const matchSearch = !query || p.name.toLowerCase().includes(query.toLowerCase());
    return matchCat && matchSearch;
  }).sort((a, b) => {
    if (sort === 'rating') return b.rating - a.rating;
    if (sort === 'price-low') return a.price - b.price;
    if (sort === 'price-high') return b.price - a.price;
    if (sort === 'name') return a.name.localeCompare(b.name);
    if (sort === 'reviews') return b.reviewCount - a.reviewCount;
    return 0;
  });

  return (
    <div className="section catalog-layout">
      {/* Filters Sidebar */}
      <aside className="filters-panel glass-card">
        <div className="search-wrap">
          <span className="search-icon"><Search size={18} /></span>
          <input 
            type="text" 
            className="search-box" 
            placeholder="Search products..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="filter-group">
          <h4>Categories</h4>
          <div>
            {CATEGORIES.map(c => (
              <button 
                key={c}
                className={`filter-btn ${c === activeCategory ? 'active' : ''}`}
                onClick={() => setSearchParams(c === 'All' ? {} : { cat: c })}
              >
                {c === 'All' ? '📦 All Products' : c}
              </button>
            ))}
          </div>
        </div>
        <div className="filter-group">
          <h4>Sort By</h4>
          <select className="sort-select" style={{width: '100%'}} value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="rating">Highest Rated</option>
            <option value="price-low">Price: Low → High</option>
            <option value="price-high">Price: High → Low</option>
            <option value="name">Name: A → Z</option>
            <option value="reviews">Most Reviewed</option>
          </select>
        </div>
      </aside>

      {/* Products Grid */}
      <main>
        <div className="catalog-header">
          <h1 style={{fontSize: '1.5rem'}}>All Products</h1>
          <span className="results-count">{filtered.length} product{filtered.length !== 1 ? 's' : ''}</span>
        </div>
        
        {filtered.length > 0 ? (
          <div className="products-grid">
            {filtered.map(product => <ProductCard key={product.id} product={product} />)}
          </div>
        ) : (
          <div style={{textAlign: 'center', padding: '3rem'}}>
            <p style={{fontSize: '3rem'}}>🔍</p>
            <h3 style={{margin: '1rem 0 0.5rem'}}>No products found</h3>
            <p style={{color: 'var(--text-secondary)'}}>Try adjusting your search or filter criteria.</p>
          </div>
        )}
      </main>
    </div>
  );
}

```

### src/pages/Home.jsx

```jsx
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

```

### src/pages/NotFound.jsx

```jsx
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

```

### src/pages/ProductDetail.jsx

```jsx
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

```

### src/pages/Scanner.jsx

```jsx
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { PRODUCTS } from '../data';

export default function Scanner() {
  const navigate = useNavigate();
  const [manualInput, setManualInput] = useState('');
  const [history, setHistory] = useState(() => JSON.parse(localStorage.getItem('scan_history') || '[]'));

  const addToHistory = useCallback((product) => {
    setHistory(prev => {
      const newHistory = [{ id: product.id, name: product.name, emoji: product.emoji, time: new Date().toLocaleString() }, ...prev].slice(0, 10);
      localStorage.setItem('scan_history', JSON.stringify(newHistory));
      return newHistory;
    });
  }, []);

  useEffect(() => {
    let scanner = null;
    try {
      scanner = new Html5QrcodeScanner("reader", {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        rememberLastUsedCamera: true
      }, false);

      scanner.render((decodedText) => {
        let productId = decodedText;
        try {
          const url = new URL(decodedText);
          productId = url.searchParams.get('id') || decodedText;
        } catch { /* Ignore */ }

        const product = PRODUCTS.find(p => p.id === productId);
        if (product) {
          addToHistory(product);
          if (scanner) scanner.clear();
          navigate(`/product?id=${product.id}`);
        } else {
          alert('Product not found in catalog.');
        }
      }, () => {});
    } catch (e) {
      console.warn("Scanner init failed", e);
    }

    return () => {
      if (scanner) scanner.clear().catch(e => console.warn(e));
    };
  }, [navigate, addToHistory]);

  const doManualSearch = () => {
    const val = manualInput.trim().toLowerCase();
    const product = PRODUCTS.find(p => p.id === val || p.name.toLowerCase().includes(val));
    if (product) {
      navigate(`/product?id=${product.id}`);
    } else {
      alert('Product not found. Try a different search.');
    }
  };

  return (
    <div className="section scanner-page">
      <div className="hero-badge" style={{marginBottom: '1rem'}}><span className="dot"></span> Camera Access Required</div>
      <h1>📷 Scan Product <span style={{background: 'var(--gradient-main)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>QR Code</span></h1>
      <p className="subtitle">Point your camera at a product's QR code to view it in AR instantly.</p>

      <div className="glass-card" style={{padding: '1.5rem', marginBottom: '1.5rem'}}>
        <div id="reader" style={{width: '100%'}}></div>
      </div>

      <div className="glass-card manual-entry" style={{padding: '1.5rem'}}>
        <h3 style={{fontSize: '1rem', marginBottom: '0.8rem'}}>Or Enter Product ID Manually</h3>
        <div style={{display: 'flex', gap: '0.5rem', justifyContent: 'center', flexWrap: 'wrap'}}>
          <input 
            type="text" 
            className="search-box" 
            placeholder="e.g. astronaut, robot, chair..." 
            style={{maxWidth: '300px'}}
            value={manualInput}
            onChange={(e) => setManualInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && doManualSearch()}
          />
          <button className="btn btn-primary btn-sm" onClick={doManualSearch}>🔍 Find</button>
        </div>
      </div>

      {history.length > 0 && (
        <div className="scan-history">
          <h3>📋 Recent Scans</h3>
          <div>
            {history.map((h, i) => (
              <div key={i} className="glass-card scan-item" style={{cursor: 'pointer'}} onClick={() => navigate(`/product?id=${h.id}`)}>
                <span>{h.emoji} {h.name}</span>
                <span className="scan-time">{h.time}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

```


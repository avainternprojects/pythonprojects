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

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

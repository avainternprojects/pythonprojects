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

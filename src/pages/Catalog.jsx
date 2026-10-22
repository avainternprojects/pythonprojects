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

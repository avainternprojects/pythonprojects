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

import PropTypes from 'prop-types';
import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { locationsApi } from '../services/api';

const CATEGORIES = [
  { key: '', label: 'Всі' },
  { key: 'tennis', label: '🎾 Теніс' },
  { key: 'football', label: '⚽ Футбол' },
  { key: 'pool', label: '🏊 Басейн' },
  { key: 'gym', label: '🏋️ Тренажерний зал' },
  { key: 'other', label: '🏟️ Інше' },
];

const STATUS_COLORS = { tennis: '#4CAF50', football: '#2196F3', pool: '#00BCD4', gym: '#FF9800', other: '#9C27B0' };

export default function LocationsPage() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams, setSearchParams] = useSearchParams();
  const category = searchParams.get('category') || '';

  useEffect(() => {
    setLoading(true);
    locationsApi.getAll(category || undefined)
      .then(r => setLocations(r.data))
      .finally(() => setLoading(false));
  }, [category]);

  return (
    <div>
      <h1 style={{ fontSize: '28px', fontWeight: 800, color: '#1a1a2e', marginBottom: '24px' }}>
        Спортивні локації
      </h1>

      {/* Filter tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '28px', flexWrap: 'wrap' }}>
        {CATEGORIES.map(cat => (
          <button key={cat.key} onClick={() => setSearchParams(cat.key ? { category: cat.key } : {})}
            style={{
              padding: '8px 16px', borderRadius: '20px', border: 'none', cursor: 'pointer',
              fontWeight: 600, fontSize: '13px', transition: 'all 0.2s',
              background: category === cat.key ? '#e94560' : '#fff',
              color: category === cat.key ? '#fff' : '#555',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
            }}>
            {cat.label}
          </button>
        ))}
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '48px', color: '#888' }}>Завантаження...</div>
      )}
      {!loading && locations.length === 0 && (
        <div style={{ textAlign: 'center', padding: '48px', color: '#888' }}>Локацій не знайдено</div>
      )}
      {!loading && locations.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
          {locations.map(loc => (
            <LocationCard key={loc.id} location={loc} />
          ))}
        </div>
      )}
    </div>
  );
}

const CATEGORY_ICONS = { tennis: '🎾', football: '⚽', pool: '🏊', gym: '🏋️', other: '🏟️' };

function LocationCard({ location }) {
  const primaryImage = location.images?.find(i => i.is_primary) || location.images?.[0];
  const color = STATUS_COLORS[location.category] || '#888';
  const categoryIcon = CATEGORY_ICONS[location.category] || '🏟️';

  return (
    <Link to={`/locations/${location.id}`} style={{ textDecoration: 'none' }}>
      <div style={{
        background: '#fff', borderRadius: '16px', overflow: 'hidden',
        boxShadow: '0 2px 12px rgba(0,0,0,0.06)', transition: 'transform 0.2s, box-shadow 0.2s',
      }}
      onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)'; }}
      onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,0,0,0.06)'; }}>

        {/* Image */}
        <div style={{ height: '180px', background: primaryImage ? '#000' : '#f0f4f8', position: 'relative', overflow: 'hidden' }}>
          {primaryImage ? (
            <img src={`http://localhost:8000${primaryImage.image_url}`} alt={location.name}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', fontSize: '48px' }}>
              {categoryIcon}
            </div>
          )}
          <div style={{
            position: 'absolute', top: '12px', left: '12px',
            background: color, color: '#fff', padding: '4px 10px',
            borderRadius: '12px', fontSize: '11px', fontWeight: 700,
          }}>
            {location.category.toUpperCase()}
          </div>
        </div>

        {/* Info */}
        <div style={{ padding: '16px' }}>
          <h3 style={{ margin: '0 0 6px', fontSize: '16px', fontWeight: 700, color: '#1a1a2e' }}>{location.name}</h3>
          <p style={{ margin: '0 0 12px', fontSize: '13px', color: '#888', lineHeight: 1.4 }}>
            📍 {location.address}
          </p>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 800, fontSize: '18px', color: '#e94560' }}>
              {location.price_per_hour} ₴<span style={{ fontSize: '12px', fontWeight: 400, color: '#888' }}>/год</span>
            </span>
            <span style={{ fontSize: '12px', color: '#888' }}>👥 до {location.capacity} осіб</span>
          </div>
        </div>
      </div>
    </Link>
  );
}
LocationCard.propTypes = {
  location: PropTypes.shape({
    id: PropTypes.number.isRequired,
    name: PropTypes.string.isRequired,
    address: PropTypes.string.isRequired,
    category: PropTypes.string.isRequired,
    price_per_hour: PropTypes.number.isRequired,
    capacity: PropTypes.number.isRequired,
    images: PropTypes.array,
  }).isRequired,
};

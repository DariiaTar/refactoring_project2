import PropTypes from 'prop-types';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';


export default function Layout({ children }) {
  const { user, logout, isAdmin, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f0f4f8', fontFamily: "'Nunito', sans-serif", display: 'flex', flexDirection: 'column' }}>
      <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet" />

      <nav style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '64px',
        boxShadow: '0 2px 20px rgba(0,0,0,0.3)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '28px' }}>🏟️</span>
          <span style={{ color: '#fff', fontWeight: 800, fontSize: '20px', letterSpacing: '-0.5px' }}>
            Sport<span style={{ color: '#e94560' }}>Book</span>
          </span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <NavLink to="/locations">Локації</NavLink>
          {isAuthenticated && <NavLink to="/my-bookings">Мої бронювання</NavLink>}
          {isAdmin && <NavLink to="/admin" accent>Адмін панель</NavLink>}

          {isAuthenticated ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: '#aaa', fontSize: '14px' }}>
                👤 {user.full_name.split(' ')[0]}
              </span>
              <button onClick={handleLogout} style={outlineBtn}>
                Вийти
              </button>
            </div>
          ) : (
            <>
              <NavLink to="/login">Увійти</NavLink>
              <Link to="/register" style={accentBtn}>Реєстрація</Link>
            </>
          )}
        </div>
      </nav>

      <main style={{ maxWidth: '1200px', width: '100%', margin: '0 auto', padding: '32px 24px', flex: 1, boxSizing: 'border-box' }}>
        {children}
      </main>

      <footer style={{
        background: '#1a1a2e',
        color: '#666',
        textAlign: 'center',
        padding: '20px',
        fontSize: '14px',
      }}>
        © 2026 SportBook UA — Бронювання спортивних локацій
      </footer>
    </div>
  );
}
Layout.propTypes = { children: PropTypes.node.isRequired };

function NavLink({ to, children, accent }) {
  return (
    <Link to={to} style={{
      color: accent ? '#e94560' : '#ccc',
      textDecoration: 'none',
      padding: '6px 12px',
      borderRadius: '6px',
      fontSize: '14px',
      fontWeight: 600,
      transition: 'all 0.2s',
    }}
    onMouseEnter={e => e.target.style.color = '#fff'}
    onMouseLeave={e => e.target.style.color = accent ? '#e94560' : '#ccc'}>
      {children}
    </Link>
  );
}
NavLink.propTypes = {
  to: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  accent: PropTypes.bool,
};
NavLink.defaultProps = { accent: false };

const outlineBtn = {
  background: 'transparent',
  border: '1px solid #555',
  color: '#ccc',
  padding: '6px 14px',
  borderRadius: '6px',
  cursor: 'pointer',
  fontSize: '13px',
  fontWeight: 600,
};

const accentBtn = {
  background: '#e94560',
  color: '#fff',
  padding: '7px 16px',
  borderRadius: '8px',
  textDecoration: 'none',
  fontSize: '13px',
  fontWeight: 700,
};

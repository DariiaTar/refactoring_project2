import PropTypes from 'prop-types';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function AuthForm({ title, fields, submitLabel, onSubmit, footer }) {
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onSubmit(form);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '420px', margin: '48px auto' }}>
      <div style={{ background: '#fff', borderRadius: '20px', padding: '40px', boxShadow: '0 4px 24px rgba(0,0,0,0.08)' }}>
        <h1 style={{ margin: '0 0 28px', fontSize: '24px', fontWeight: 800, color: '#1a1a2e', textAlign: 'center' }}>
          {title}
        </h1>
        <form onSubmit={handleSubmit}>
          {fields.map(f => (
            <div key={f.name} style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#555', marginBottom: '6px' }}>
                {f.label}
              </label>
              <input
                type={f.type || 'text'}
                placeholder={f.placeholder}
                pattern={f.pattern}
                required={f.required !== false}
                onChange={e => setForm(prev => ({ ...prev, [f.name]: e.target.value }))}
                style={{
                  width: '100%', padding: '10px 14px', border: '1.5px solid #e0e0e0',
                  borderRadius: '10px', fontSize: '14px', outline: 'none',
                  boxSizing: 'border-box', transition: 'border-color 0.2s',
                }}
                onFocus={e => e.target.style.borderColor = '#e94560'}
                onBlur={e => e.target.style.borderColor = '#e0e0e0'}
                title={f.pattern && f.name === 'phone' ? 'Введіть коректний номер телефону (7-15 цифр, можна з +)' : ''}
              />
            </div>
          ))}
          <button type="submit" disabled={loading} style={{
            width: '100%', padding: '12px', background: loading ? '#ccc' : '#e94560',
            color: '#fff', border: 'none', borderRadius: '10px', fontWeight: 700,
            fontSize: '15px', cursor: loading ? 'not-allowed' : 'pointer', marginTop: '8px',
          }}>
            {loading ? 'Завантаження...' : submitLabel}
          </button>
        </form>
        <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '13px', color: '#888' }}>
          {footer}
        </div>
      </div>
    </div>
  );
}

AuthForm.propTypes = {
  title: PropTypes.string.isRequired,
  fields: PropTypes.arrayOf(PropTypes.shape({
    name: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    type: PropTypes.string,
    placeholder: PropTypes.string,
    pattern: PropTypes.string,
    required: PropTypes.bool,
  })).isRequired,
  submitLabel: PropTypes.string.isRequired,
  onSubmit: PropTypes.func.isRequired,
  footer: PropTypes.node.isRequired,
};

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (form) => {
    try {
      const user = await login(form.email, form.password);
      toast.success(`Вітаємо, ${user.full_name.split(' ')[0]}!`);
      navigate(user.role === 'admin' ? '/admin' : '/locations');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Помилка входу');
    }
  };

  return (
    <AuthForm
      title="🏟️ Вхід"
      fields={[
        { name: 'email', label: 'Email', type: 'email', placeholder: 'your@email.com' },
        { name: 'password', label: 'Пароль', type: 'password', placeholder: '••••••' },
      ]}
      submitLabel="Увійти"
      onSubmit={handleLogin}
      footer={<>Немає акаунту? <Link to="/register" style={{ color: '#e94560', fontWeight: 700 }}>Зареєструватись</Link></>}
    />
  );
}

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (form) => {
    try {
      await register(form);
      toast.success('Реєстрація успішна!');
      navigate('/locations');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Помилка реєстрації');
    }
  };

  return (
    <AuthForm
      title="🏟️ Реєстрація"
      fields={[
        { name: 'full_name', label: "Повне ім'я", placeholder: 'Іван Петренко' },
        { name: 'email', label: 'Email', type: 'email', placeholder: 'your@email.com' },
        { name: 'phone', label: 'Телефон', placeholder: '+380501234567', type: 'tel', pattern: '^[+]?[0-9]{7,15}$', required: true },
        { name: 'password', label: 'Пароль', type: 'password', placeholder: 'мінімум 6 символів' },
      ]}
      submitLabel="Зареєструватись"
      onSubmit={handleRegister}
      footer={<>Вже є акаунт? <Link to="/login" style={{ color: '#e94560', fontWeight: 700 }}>Увійти</Link></>}
    />
  );
}

export default LoginPage;

import PropTypes from 'prop-types';
import { format } from 'date-fns';
import { uk } from 'date-fns/locale';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { bookingsApi } from '../services/api';

const STATUS_LABELS = {
  pending_payment: { label: 'Очікує оплати', color: '#FF9800', bg: '#FFF3E0' },
  confirmed: { label: 'Підтверджено', color: '#4CAF50', bg: '#E8F5E9' },
  cancelled: { label: 'Скасовано', color: '#f44336', bg: '#FFEBEE' },
  completed: { label: 'Завершено', color: '#888', bg: '#f5f5f5' },
};

const ALL_STATUSES = [
  { value: 'pending_payment', label: 'Очікує оплати' },
  { value: 'confirmed', label: 'Підтверджено' },
  { value: 'cancelled', label: 'Скасовано' },
  { value: 'completed', label: 'Завершено' },
];

export default function BookingDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState('');
  const [saving, setSaving] = useState(false);
  const [paying, setPaying] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  const load = () => {
    setLoading(true);
    bookingsApi.getOne(id)
      .then(r => {
        setBooking(r.data);
        setNewStatus(r.data.status);
      })
      .catch(() => toast.error('Бронювання не знайдено'))
      .finally(() => setLoading(false));
  };

  useEffect(load, [id]);

  const handleStatusSave = async () => {
    if (newStatus === booking.status) return;
    setSaving(true);
    try {
      await bookingsApi.updateStatus(id, newStatus);
      toast.success('Статус оновлено');
      load();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Помилка');
    } finally {
      setSaving(false);
    }
  };

  const handlePay = async () => {
    setPaying(true);
    try {
      await bookingsApi.pay(id);
      toast.success('Оплата успішна! Бронювання підтверджено.');
      load();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Помилка оплати');
    } finally {
      setPaying(false);
    }
  };

  const handleCancel = async () => {
    if (!globalThis.confirm('Скасувати бронювання?')) return;
    setCancelling(true);
    try {
      await bookingsApi.cancel(id);
      toast.success('Бронювання скасовано');
      load();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Помилка');
    } finally {
      setCancelling(false);
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '64px', color: '#888' }}>Завантаження...</div>;
  }

  if (!booking) {
    return (
      <div style={{ textAlign: 'center', padding: '64px' }}>
        <p style={{ color: '#888' }}>Бронювання не знайдено</p>
        <button onClick={() => navigate(-1)} style={btnGray}>Назад</button>
      </div>
    );
  }

  const st = STATUS_LABELS[booking.status] || STATUS_LABELS.pending_payment;
  const isPending = booking.status === 'pending_payment';
  const isCancelled = booking.status === 'cancelled';
  const statusChanged = newStatus !== booking.status;

  return (
    <div style={{ maxWidth: '680px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '28px' }}>
        <button onClick={() => navigate(-1)} style={{ ...btnGray, padding: '8px 14px' }}>← Назад</button>
        <h1 style={{ margin: 0, fontSize: '26px', fontWeight: 800, color: '#1a1a2e' }}>
          Бронювання #{booking.id}
        </h1>
      </div>

      {/* Status badge */}
      <div style={{ marginBottom: '24px' }}>
        <span style={{
          background: st.bg, color: st.color,
          padding: '8px 18px', borderRadius: '24px', fontSize: '14px', fontWeight: 700,
        }}>
          {st.label}
        </span>
      </div>

      {/* Main card */}
      <div style={card}>
        {/* Location */}
        <Section title="Локація">
          <InfoRow label="Назва" value={booking.location_name} />
          <InfoRow label="Адреса" value={booking.location_address} />
        </Section>

        {/* Time */}
        <Section title="Час">
          <InfoRow
            label="Початок"
            value={format(new Date(booking.start_time), 'd MMMM yyyy, HH:mm', { locale: uk })}
          />
          <InfoRow
            label="Кінець"
            value={format(new Date(booking.end_time), 'd MMMM yyyy, HH:mm', { locale: uk })}
          />
        </Section>

        {/* Price */}
        <Section title="Оплата">
          <InfoRow
            label="Сума"
            value={<span style={{ fontWeight: 800, color: '#e94560', fontSize: '18px' }}>{booking.total_price} ₴</span>}
          />
          <InfoRow
            label="Статус оплати"
            value={getPaymentStatus(isPending, isCancelled)}
          />
        </Section>

        {/* Customer */}
        <Section title="Клієнт">
          <InfoRow label="Ім'я" value={booking.user_full_name} />
          {booking.user_phone && <InfoRow label="Телефон" value={booking.user_phone} />}
          {booking.guest_name && <InfoRow label="Гість" value={booking.guest_name} />}
          {booking.guest_email && <InfoRow label="Email гостя" value={booking.guest_email} />}
          {booking.guest_phone && <InfoRow label="Телефон гостя" value={booking.guest_phone} />}
        </Section>

        {/* Notes */}
        {booking.notes && (
          <Section title="Коментар">
            <div style={{
              background: '#fff3e0', borderLeft: '3px solid #FF9800',
              padding: '12px 16px', borderRadius: '8px', color: '#555', fontSize: '14px',
            }}>
              {booking.notes}
            </div>
          </Section>
        )}

        {/* Meta */}
        <Section title="Деталі">
          <InfoRow
            label="Створено"
            value={format(new Date(booking.created_at), 'd MMMM yyyy, HH:mm', { locale: uk })}
          />
          <InfoRow label="ID слоту" value={`#${booking.slot_id}`} />
        </Section>
      </div>

      {/* Admin: status change */}
      {isAdmin && (
        <div style={{ ...card, marginTop: '16px' }}>
          <h3 style={{ margin: '0 0 16px', fontWeight: 700, fontSize: '16px', color: '#1a1a2e' }}>
            Змінити статус
          </h3>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
            <select
              value={newStatus}
              onChange={e => setNewStatus(e.target.value)}
              style={selectStyle}
            >
              {ALL_STATUSES.map(s => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
            <button
              onClick={handleStatusSave}
              disabled={!statusChanged || saving}
              style={{
                ...btnRed,
                opacity: !statusChanged || saving ? 0.5 : 1,
                cursor: !statusChanged || saving ? 'not-allowed' : 'pointer',
              }}
            >
              {saving ? 'Збереження...' : 'Зберегти статус'}
            </button>
          </div>
        </div>
      )}

      {/* User actions */}
      {!isCancelled && (
        <div style={{ display: 'flex', gap: '12px', marginTop: '20px', flexWrap: 'wrap' }}>
          {isPending && (
            <button
              onClick={handlePay}
              disabled={paying}
              style={{ ...btnGreen, opacity: paying ? 0.6 : 1 }}
            >
              {paying ? 'Обробка...' : '💳 Оплатити'}
            </button>
          )}
          {isPending && (
            <button
              onClick={handleCancel}
              disabled={cancelling}
              style={{ ...btnOutlineRed, opacity: cancelling ? 0.6 : 1 }}
            >
              {cancelling ? 'Скасування...' : 'Скасувати'}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function getPaymentStatus(isPending, isCancelled) {
  if (isPending) return 'Не оплачено';
  if (isCancelled) return 'Скасовано';
  return 'Оплачено';
}

function Section({ title, children }) {
  return (
    <div style={{ marginBottom: '20px' }}>
      <div style={{ fontSize: '11px', fontWeight: 700, color: '#aaa', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '10px' }}>
        {title}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {children}
      </div>
      <div style={{ borderBottom: '1px solid #f0f0f0', marginTop: '20px' }} />
    </div>
  );
}
Section.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};

function InfoRow({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ color: '#888', fontSize: '14px' }}>{label}</span>
      <span style={{ color: '#1a1a2e', fontSize: '14px', fontWeight: 500 }}>{value}</span>
    </div>
  );
}
InfoRow.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.node.isRequired,
};

const card = {
  background: '#fff', borderRadius: '16px', padding: '24px 28px',
  boxShadow: '0 2px 12px rgba(0,0,0,0.07)',
};
const btnRed = {
  background: '#e94560', color: '#fff', border: 'none',
  borderRadius: '10px', padding: '10px 22px', fontWeight: 700, fontSize: '14px', cursor: 'pointer',
};
const btnGreen = {
  background: '#4CAF50', color: '#fff', border: 'none',
  borderRadius: '10px', padding: '10px 22px', fontWeight: 700, fontSize: '14px', cursor: 'pointer',
};
const btnGray = {
  background: '#fff', color: '#555', border: '1.5px solid #e0e0e0',
  borderRadius: '10px', padding: '8px 16px', fontWeight: 600, fontSize: '13px', cursor: 'pointer',
};
const btnOutlineRed = {
  background: '#fff', color: '#f44336', border: '1.5px solid #f44336',
  borderRadius: '10px', padding: '10px 22px', fontWeight: 700, fontSize: '14px', cursor: 'pointer',
};
const selectStyle = {
  padding: '9px 12px', border: '1.5px solid #e0e0e0', borderRadius: '8px',
  fontSize: '13px', outline: 'none', minWidth: '200px',
};

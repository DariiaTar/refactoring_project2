import { format } from 'date-fns';
import { uk } from 'date-fns/locale';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { bookingsApi } from '../services/api';

const STATUS_LABELS = {
  pending_payment: { label: 'Очікує оплати', color: '#FF9800', bg: '#FFF3E0' },
  confirmed: { label: 'Підтверджено', color: '#4CAF50', bg: '#E8F5E9' },
  cancelled: { label: 'Скасовано', color: '#f44336', bg: '#FFEBEE' },
  completed: { label: 'Завершено', color: '#888', bg: '#f5f5f5' },
};

export default function MyBookingsPage() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const load = () => {
    bookingsApi.getMy()
      .then(r => setBookings(r.data))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleCancel = async (id) => {
    if (!globalThis.confirm('Скасувати бронювання?')) return;
    try {
      await bookingsApi.cancel(id);
      toast.success('Бронювання скасовано');
      load();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Помилка');
    }
  };

  const handlePay = async (id) => {
    try {
      await bookingsApi.pay(id);
      toast.success('Бронювання оплачено');
      load();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Помилка оплати');
    }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '48px', color: '#888' }}>Завантаження...</div>;

  return (
    <div>
      <h1 style={{ fontSize: '28px', fontWeight: 800, color: '#1a1a2e', marginBottom: '24px' }}>
        Мої бронювання
      </h1>

      {bookings.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '64px', background: '#fff', borderRadius: '16px', color: '#888' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📅</div>
          <p>У вас ще немає бронювань</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {bookings.map(b => {
            const st = STATUS_LABELS[b.status] || STATUS_LABELS.pending_payment;
            return (
              <div key={b.id} style={{
                background: '#fff', borderRadius: '16px', padding: '20px 24px',
                boxShadow: '0 2px 12px rgba(0,0,0,0.06)',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              }}>
                <div>
                  <div style={{ fontWeight: 700, color: '#1a1a2e', fontSize: '16px', marginBottom: '4px' }}>
                    Бронювання #{b.id}
                  </div>
                  <div style={{ color: '#888', fontSize: '13px', marginBottom: '4px' }}>
                    Слот: #{b.slot_id} · {format(new Date(b.created_at), 'd MMM yyyy', { locale: uk })}
                  </div>
                  <div style={{ fontWeight: 700, color: '#e94560' }}>{b.total_price} ₴</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{
                    background: st.bg, color: st.color, padding: '5px 12px',
                    borderRadius: '20px', fontSize: '12px', fontWeight: 700,
                  }}>
                    {st.label}
                  </span>
                  <button onClick={() => navigate(`/bookings/${b.id}`)} style={{
                    background: '#e94560', border: 'none', color: '#fff',
                    padding: '6px 14px', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, fontSize: '13px',
                  }}>
                    Деталі
                  </button>
                  {b.status === 'pending_payment' && (
                    <button onClick={() => handlePay(b.id)} style={{
                      background: '#4CAF50', border: 'none', color: '#fff',
                      padding: '6px 14px', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, fontSize: '13px',
                    }}>
                      Оплатити
                    </button>
                  )}
                  {b.status === 'pending_payment' && (
                    <button onClick={() => handleCancel(b.id)} style={{
                      background: '#fff', border: '1.5px solid #f44336', color: '#f44336',
                      padding: '6px 14px', borderRadius: '8px', cursor: 'pointer', fontWeight: 600, fontSize: '13px',
                    }}>
                      Скасувати
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

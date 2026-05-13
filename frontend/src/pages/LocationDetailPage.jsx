import PropTypes from 'prop-types';
import { format, isBefore, isSameDay, isToday } from 'date-fns';
import { uk } from 'date-fns/locale';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { bookingsApi, locationsApi, slotsApi } from '../services/api';

export default function LocationDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [location, setLocation] = useState(null);
  const [allSlots, setAllSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [activeImage, setActiveImage] = useState(0);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);

  useEffect(() => {
    Promise.all([
      locationsApi.getById(id),
      slotsApi.getAvailable(id),
    ]).then(([locRes, slotsRes]) => {
      setLocation(locRes.data);
      setAllSlots(slotsRes.data);
    }).finally(() => setLoading(false));
  }, [id]);

  const handleBook = async (slotId) => {
    if (!isAuthenticated) {
      toast.error('Увійдіть, щоб забронювати');
      navigate('/login');
      return;
    }
    setBooking(slotId);
    try {
      await bookingsApi.create({ slot_id: slotId });
      toast.success('Успішно заброньовано! Очікуйте підтвердження оплати.');
      const res = await slotsApi.getAvailable(id);
      setAllSlots(res.data);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Помилка бронювання');
    } finally {
      setBooking(false);
    }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '48px', color: '#888' }}>Завантаження...</div>;
  if (!location) return <div style={{ textAlign: 'center', padding: '48px', color: '#888' }}>Локацію не знайдено</div>;

  const images = location.images || [];

  const CATEGORY_ICONS = { tennis: '🎾', football: '⚽', pool: '🏊', gym: '🏋️' };
  const categoryIcon = CATEGORY_ICONS[location.category] || '🏋️';

  return (
    <div>
      <button onClick={() => navigate(-1)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#e94560', fontWeight: 700, fontSize: '14px', marginBottom: '20px', padding: 0 }}>
        ← Назад
      </button>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: '28px' }}>
        {/* Left: Photos + Info */}
        <div>
          {/* Gallery */}
          <div style={{ borderRadius: '20px', overflow: 'hidden', marginBottom: '16px', background: '#f0f4f8', height: '360px' }}>
            {images.length > 0 ? (
              <img src={`http://localhost:8000${images[activeImage]?.image_url}`} alt={location.name}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', fontSize: '80px' }}>
                {categoryIcon}
              </div>
            )}
          </div>
          {images.length > 1 && (
            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
              {images.map((img, i) => (
                <button
                  key={img.id}
                  onClick={() => setActiveImage(i)}
                  style={{ cursor: 'pointer', border: i === activeImage ? '3px solid #e94560' : '3px solid transparent', padding: 0, background: 'none', borderRadius: '8px' }}
                >
                  <img
                    src={`http://localhost:8000${img.image_url}`}
                    alt={`Gallery image ${i + 1}`}
                    style={{ width: '72px', height: '56px', objectFit: 'cover', borderRadius: '6px', display: 'block' }}
                  />
                </button>
              ))}
            </div>
          )}

          {/* Details */}
          <div style={{ background: '#fff', borderRadius: '16px', padding: '24px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <h1 style={{ margin: '0 0 8px', fontSize: '26px', fontWeight: 800, color: '#1a1a2e' }}>{location.name}</h1>
            <p style={{ margin: '0 0 16px', color: '#888', fontSize: '14px' }}>📍 {location.address}</p>
            {location.description && (
              <p style={{ color: '#555', lineHeight: 1.6, margin: '0 0 16px' }}>{location.description}</p>
            )}
            <div style={{ display: 'flex', gap: '16px' }}>
              <InfoChip label="Ціна" value={`${location.price_per_hour} ₴/год`} />
              <InfoChip label="Місткість" value={`до ${location.capacity} осіб`} />
            </div>
          </div>
        </div>

        {/* Right: Slots */}
        <div>
          <div style={{ background: '#fff', borderRadius: '16px', padding: '24px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)', position: 'sticky', top: '80px' }}>
            <h2 style={{ margin: '0 0 20px', fontSize: '18px', fontWeight: 800, color: '#1a1a2e' }}>
              Бронювання
            </h2>
            
            {/* Date Picker */}
            <div style={{ marginBottom: '20px', position: 'relative' }}>
              <button
                onClick={() => setShowDatePicker(!showDatePicker)}
                style={{
                  width: '100%',
                  padding: '12px 14px',
                  border: '1.5px solid #e94560',
                  borderRadius: '12px',
                  background: '#fff',
                  color: '#1a1a2e',
                  fontSize: '14px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                📅 {format(selectedDate, 'd MMMM yyyy', { locale: uk })}
              </button>
              
              {showDatePicker && (
                <DatePickerCalendar
                  selectedDate={selectedDate}
                  onDateSelect={(date) => {
                    setSelectedDate(date);
                    setShowDatePicker(false);
                  }}
                  onClose={() => setShowDatePicker(false)}
                />
              )}
            </div>
            
            {/* Available Slots for Selected Date */}
            {allSlots.length === 0 ? (
              <p style={{ color: '#888', textAlign: 'center', padding: '24px 0' }}>Немає доступних слотів</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '480px', overflowY: 'auto' }}>
                {allSlots.filter(slot => {
                  const slotDate = new Date(slot.start_time);
                  return isSameDay(slotDate, selectedDate);
                }).length === 0 ? (
                  <p style={{ color: '#888', textAlign: 'center', padding: '24px 0', fontSize: '14px' }}>
                    На цю дату слотів немає
                  </p>
                ) : (
                  allSlots.filter(slot => {
                    const slotDate = new Date(slot.start_time);
                    return isSameDay(slotDate, selectedDate);
                  }).map(slot => {
                    const start = new Date(slot.start_time);
                    const end = new Date(slot.end_time);
                    const hours = (end - start) / 3600000;
                    const price = location.price_per_hour * hours;
                    return (
                      <div key={slot.id} style={{
                        border: '1.5px solid #f0f4f8', borderRadius: '12px', padding: '12px 14px',
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      }}>
                        <div>
                          <div style={{ fontWeight: 700, color: '#1a1a2e', fontSize: '14px' }}>
                            {format(start, 'HH:mm')} – {format(end, 'HH:mm')}
                          </div>
                          <div style={{ color: '#e94560', fontSize: '13px', fontWeight: 700 }}>{price} ₴</div>
                        </div>
                        <button onClick={() => handleBook(slot.id)}
                          disabled={booking === slot.id}
                          style={{
                            background: booking === slot.id ? '#ccc' : '#e94560',
                            color: '#fff', border: 'none', borderRadius: '8px',
                            padding: '8px 14px', cursor: booking === slot.id ? 'not-allowed' : 'pointer',
                            fontWeight: 700, fontSize: '13px',
                          }}>
                          {booking === slot.id ? '...' : 'Забронювати'}
                        </button>
                      </div>
                    );
                  })
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoChip({ label, value }) {
  return (
    <div style={{ background: '#f0f4f8', borderRadius: '10px', padding: '10px 16px' }}>
      <div style={{ fontSize: '11px', color: '#888', marginBottom: '2px' }}>{label}</div>
      <div style={{ fontSize: '15px', fontWeight: 700, color: '#1a1a2e' }}>{value}</div>
    </div>
  );
}
InfoChip.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.node.isRequired,
};

function DatePickerCalendar({ selectedDate, onDateSelect, onClose }) {
  const [viewMonth, setViewMonth] = useState(new Date(selectedDate.getFullYear(), selectedDate.getMonth(), 1));

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const getDaysInMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const handlePrevMonth = () => {
    setViewMonth(new Date(viewMonth.getFullYear(), viewMonth.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setViewMonth(new Date(viewMonth.getFullYear(), viewMonth.getMonth() + 1, 1));
  };

  const days = [];
  const daysInMonth = getDaysInMonth(viewMonth);
  const firstDay = getFirstDayOfMonth(viewMonth);

  for (let i = 0; i < firstDay; i++) {
    days.push(null);
  }
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i);
  }

  return (
    <div style={{
      position: 'absolute',
      top: '50px',
      left: 0,
      right: 0,
      background: '#fff',
      border: '1.5px solid #e94560',
      borderRadius: '12px',
      padding: '16px',
      zIndex: 1000,
      boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
    }}>
      {/* Month/Year Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <button
          onClick={handlePrevMonth}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '18px',
            cursor: 'pointer',
            color: '#e94560',
            fontWeight: 700,
          }}
        >
          ←
        </button>
        <div style={{ fontWeight: 700, color: '#1a1a2e', fontSize: '14px' }}>
          {format(viewMonth, 'MMMM yyyy', { locale: uk })}
        </div>
        <button
          onClick={handleNextMonth}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '18px',
            cursor: 'pointer',
            color: '#e94560',
            fontWeight: 700,
          }}
        >
          →
        </button>
      </div>

      {/* Day Labels */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px', marginBottom: '8px' }}>
        {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'].map((day) => (
          <div
            key={day}
            style={{
              textAlign: 'center',
              fontSize: '11px',
              fontWeight: 700,
              color: '#888',
              padding: '4px 0',
            }}
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px' }}>
        {days.map((day, i) => {
          if (day === null) {
            return <div key={`empty-${i}`} />;
          }

          const date = new Date(viewMonth.getFullYear(), viewMonth.getMonth(), day);
          const isSelected = isSameDay(date, selectedDate);
          const isDisabled = isBefore(date, today);
          const isTodayDate = isToday(date);

          return (
            <button
              key={day}
              onClick={() => !isDisabled && onDateSelect(date)}
              style={{
                padding: '8px 4px',
                border: isSelected ? '2px solid #e94560' : '1px solid #f0f4f8',
                borderRadius: '8px',
                background: isSelected ? '#e94560' : isTodayDate ? '#fff3cd' : '#fff',
                color: isSelected ? '#fff' : isDisabled ? '#ddd' : '#1a1a2e',
                cursor: isDisabled ? 'not-allowed' : 'pointer',
                fontWeight: isSelected || isTodayDate ? 700 : 600,
                fontSize: '12px',
                opacity: isDisabled ? 0.5 : 1,
              }}
              disabled={isDisabled}
            >
              {day}
            </button>
          );
        })}
      </div>

      {/* Close Button */}
      <button
        type="button"
        onClick={onClose}
        style={{
          width: '100%',
          marginTop: '12px',
          padding: '8px',
          background: '#f0f4f8',
          border: 'none',
          borderRadius: '8px',
          color: '#1a1a2e',
          fontWeight: 600,
          fontSize: '12px',
          cursor: 'pointer',
        }}
      >
        Закрити
      </button>
    </div>
  );
}
DatePickerCalendar.propTypes = {
  selectedDate: PropTypes.instanceOf(Date).isRequired,
  onDateSelect: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
};

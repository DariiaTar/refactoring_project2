import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { bookingsApi, locationsApi, slotsApi, usersApi } from '../services/api';

const TABS = ['Локації', 'Слоти', 'Бронювання', 'Користувачі'];
const CATEGORIES = ['tennis', 'football', 'pool', 'gym', 'other'];
const STATUS_LABELS = {
  pending_payment: 'Очікує оплати', confirmed: 'Підтверджено',
  cancelled: 'Скасовано', completed: 'Завершено',
};

export default function AdminPage() {
  const [tab, setTab] = useState(0);
  const [locations, setLocations] = useState([]);
  const [slots, setSlots] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [users, setUsers] = useState([]);

  useEffect(() => {
    locationsApi.getAll(undefined).then(r => setLocations(r.data));
    bookingsApi.getAll().then(r => setBookings(r.data));
    usersApi.getAll().then(r => setUsers(r.data));
  }, []);

  const loadSlotsForLocation = (locationId) => {
    slotsApi.getByLocation(locationId).then(r => setSlots(r.data));
  };

  return (
    <div>
      <h1 style={{ fontSize: '28px', fontWeight: 800, color: '#1a1a2e', marginBottom: '24px' }}>
        ⚙️ Адміністрування
      </h1>

      <div style={{ display: 'flex', gap: '0', marginBottom: '28px', background: '#fff', borderRadius: '12px', padding: '4px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)', width: 'fit-content' }}>
        {TABS.map((t, i) => (
          <button key={t} onClick={() => setTab(i)} style={{
            padding: '10px 20px', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '14px',
            borderRadius: '10px', transition: 'all 0.2s',
            background: tab === i ? '#e94560' : 'transparent',
            color: tab === i ? '#fff' : '#555',
          }}>{t}</button>
        ))}
      </div>

      {tab === 0 && <LocationsTab locations={locations} setLocations={setLocations} />}
      {tab === 1 && <SlotsTab locations={locations} slots={slots} loadSlots={loadSlotsForLocation} setSlots={setSlots} />}
      {tab === 2 && <BookingsTab bookings={bookings} setBookings={setBookings} />}
      {tab === 3 && <UsersTab users={users} setUsers={setUsers} />}
    </div>
  );
}

// ---- LOCATIONS TAB ----
function LocationsTab({ locations, setLocations }) {
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ name: '', description: '', category: 'tennis', address: '', price_per_hour: '', capacity: 10 });

  const reload = () => locationsApi.getAll(undefined).then(r => setLocations(r.data));

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {
        ...form,
        price_per_hour: Number.parseFloat(form.price_per_hour),
        capacity: Number.parseInt(form.capacity, 10),
      };
      if (editing) {
        await locationsApi.update(editing.id, data);
        toast.success('Локацію оновлено');
      } else {
        await locationsApi.create(data);
        toast.success('Локацію створено');
      }
      setShowForm(false); setEditing(null);
      reload();
    } catch (submitError) { toast.error(submitError.response?.data?.detail || 'Помилка'); }
  };

  const handleDelete = async (id) => {
    if (!globalThis.confirm('Видалити локацію?')) return;
    await locationsApi.delete(id);
    toast.success('Видалено');
    reload();
  };

  const handleUpload = async (locationId, file, isPrimary) => {
    try {
      await locationsApi.uploadImage(locationId, file, isPrimary);
      toast.success('Фото завантажено');
      reload();
    } catch (uploadError) { toast.error(uploadError?.response?.data?.detail || 'Помилка завантаження'); }
  };

  const handleDeleteImage = async (imageId) => {
    await locationsApi.deleteImage(imageId);
    toast.success('Фото видалено');
    reload();
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>Локації ({locations.length})</h2>
        <button onClick={() => { setShowForm(true); setEditing(null); setForm({ name: '', description: '', category: 'tennis', address: '', price_per_hour: '', capacity: 10 }); }}
          style={btnRed}>+ Додати локацію</button>
      </div>

      {showForm && (
        <div style={modalOverlay}>
          <div style={modalBox}>
            <h3 style={{ margin: '0 0 20px', fontWeight: 700 }}>{editing ? 'Редагувати' : 'Нова локація'}</h3>
            <form onSubmit={handleSubmit}>
              {[
                { name: 'name', label: 'Назва' },
                { name: 'description', label: 'Опис', required: false },
                { name: 'address', label: 'Адреса' },
                { name: 'price_per_hour', label: 'Ціна (₴/год)', type: 'number' },
                { name: 'capacity', label: 'Місткість', type: 'number' },
              ].map(f => (
                <div key={f.name} style={{ marginBottom: '12px' }}>
                  <label htmlFor={`field-${f.name}`} style={labelStyle}>{f.label}</label>
                  <input
                    id={`field-${f.name}`}
                    type={f.type || 'text'}
                    value={form[f.name] || ''}
                    required={f.required !== false}
                    onChange={e => setForm(p => ({ ...p, [f.name]: e.target.value }))}
                    style={inputStyle}
                  />
                </div>
              ))}
              <div style={{ marginBottom: '12px' }}>
                <label htmlFor="field-category" style={labelStyle}>Категорія</label>
                <select id="field-category" value={form.category} onChange={e => setForm(p => ({ ...p, category: e.target.value }))} style={inputStyle}>
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
                <button type="submit" style={btnRed}>Зберегти</button>
                <button type="button" onClick={() => setShowForm(false)} style={btnGray}>Скасувати</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {locations.map(loc => (
          <div key={loc.id} style={cardStyle}>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, color: '#1a1a2e', marginBottom: '4px' }}>{loc.name}</div>
              <div style={{ color: '#888', fontSize: '13px' }}>{loc.address} · {loc.category} · {loc.price_per_hour}₴/год</div>

              <div style={{ display: 'flex', gap: '6px', marginTop: '10px', flexWrap: 'wrap' }}>
                {(loc.images || []).map(img => (
                  <div key={img.id} style={{ position: 'relative' }}>
                    <img src={`http://localhost:8000${img.image_url}`} alt=""
                      style={{ width: '56px', height: '44px', objectFit: 'cover', borderRadius: '6px', border: img.is_primary ? '2px solid #e94560' : '2px solid transparent' }} />
                    <button onClick={() => handleDeleteImage(img.id)}
                      style={{ position: 'absolute', top: -4, right: -4, background: '#f44336', color: '#fff', border: 'none', borderRadius: '50%', width: '16px', height: '16px', cursor: 'pointer', fontSize: '10px', padding: 0 }}>
                      ×
                    </button>
                  </div>
                ))}
                <label htmlFor={`upload-${loc.id}`} style={{ width: '56px', height: '44px', background: '#f0f4f8', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', fontSize: '20px', color: '#888' }}>
                  <span>+</span>
                  <input
                    id={`upload-${loc.id}`}
                    type="file"
                    accept="image/*"
                    style={{ display: 'none' }}
                    onChange={e => e.target.files[0] && handleUpload(loc.id, e.target.files[0], (loc.images || []).length === 0)}
                  />
                </label>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button onClick={() => { setEditing(loc); setForm({ name: loc.name, description: loc.description || '', category: loc.category, address: loc.address, price_per_hour: loc.price_per_hour, capacity: loc.capacity }); setShowForm(true); }}
                style={btnGray}>✏️ Ред.</button>
              <button onClick={() => handleDelete(loc.id)} style={{ ...btnGray, color: '#f44336', borderColor: '#f44336' }}>🗑️</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
LocationsTab.propTypes = {
  locations: PropTypes.array.isRequired,
  setLocations: PropTypes.func.isRequired,
};

// ---- SLOTS TAB ----
function SlotsTab({ locations, slots, loadSlots, setSlots }) {
  const [selectedLoc, setSelectedLoc] = useState('');
  const [form, setForm] = useState({ start_time: '', end_time: '' });

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await slotsApi.create({ location_id: Number.parseInt(selectedLoc, 10), start_time: form.start_time, end_time: form.end_time });
      toast.success('Слот створено');
      loadSlots(selectedLoc);
    } catch (createError) { toast.error(createError.response?.data?.detail || 'Помилка'); }
  };

  const handleDelete = async (id) => {
    try {
      await slotsApi.delete(id);
      toast.success('Слот видалено');
      loadSlots(selectedLoc);
    } catch (deleteError) { toast.error(deleteError.response?.data?.detail || 'Не можна видалити заброньований слот'); }
  };

  const STATUS_COLORS = { available: '#4CAF50', booked: '#f44336', blocked: '#888' };

  return (
    <div>
      <div style={{ background: '#fff', borderRadius: '16px', padding: '20px', marginBottom: '20px', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
        <h3 style={{ margin: '0 0 16px', fontWeight: 700 }}>Нові слоти</h3>
        <form onSubmit={handleCreate} style={{ display: 'flex', gap: '12px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div>
            <label htmlFor="slot-location" style={labelStyle}>Локація</label>
            <select id="slot-location" value={selectedLoc} onChange={e => { setSelectedLoc(e.target.value); if (e.target.value) loadSlots(e.target.value); }}
              style={{ ...inputStyle, width: '200px' }} required>
              <option value="">Оберіть...</option>
              {locations.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="slot-start" style={labelStyle}>Початок</label>
            <input id="slot-start" type="datetime-local" value={form.start_time} onChange={e => setForm(p => ({ ...p, start_time: e.target.value }))} style={inputStyle} required />
          </div>
          <div>
            <label htmlFor="slot-end" style={labelStyle}>Кінець</label>
            <input id="slot-end" type="datetime-local" value={form.end_time} onChange={e => setForm(p => ({ ...p, end_time: e.target.value }))} style={inputStyle} required />
          </div>
          <button type="submit" style={btnRed}>+ Додати слот</button>
        </form>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {slots.map(slot => (
          <div key={slot.id} style={{ ...cardStyle, padding: '12px 16px' }}>
            <div style={{ flex: 1 }}>
              <span style={{ fontWeight: 600 }}>
                {new Date(slot.start_time).toLocaleString('uk-UA')} → {new Date(slot.end_time).toLocaleString('uk-UA')}
              </span>
            </div>
            <span style={{
              background: STATUS_COLORS[slot.status] + '20', color: STATUS_COLORS[slot.status],
              padding: '3px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 700, marginRight: '12px',
            }}>{slot.status}</span>
            {slot.status !== 'booked' && (
              <button onClick={() => handleDelete(slot.id)} style={{ ...btnGray, color: '#f44336' }}>🗑️</button>
            )}
          </div>
        ))}
        {slots.length === 0 && selectedLoc && <p style={{ color: '#888', textAlign: 'center' }}>Немає слотів</p>}
        {!selectedLoc && <p style={{ color: '#888', textAlign: 'center' }}>Оберіть локацію вище</p>}
      </div>
    </div>
  );
}
SlotsTab.propTypes = {
  locations: PropTypes.array.isRequired,
  slots: PropTypes.array.isRequired,
  loadSlots: PropTypes.func.isRequired,
  setSlots: PropTypes.func.isRequired,
};

// ---- BOOKINGS TAB ----
function BookingsTab({ bookings, setBookings }) {
  const navigate = useNavigate();

  const handleStatus = async (id, status) => {
    await bookingsApi.updateStatus(id, status);
    toast.success('Статус оновлено');
    bookingsApi.getAll().then(r => setBookings(r.data));
  };

  const groupedByLocation = bookings.reduce((acc, b) => {
    const locName = b.location_name || 'Невідома локація';
    if (!acc[locName]) {
      acc[locName] = [];
    }
    acc[locName].push(b);
    return acc;
  }, {});

  return (
    <div>
      <h2 style={{ margin: '0 0 16px', fontSize: '18px', fontWeight: 700 }}>Всі бронювання ({bookings.length})</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {Object.entries(groupedByLocation).map(([locationName, locationBookings]) => (
          <div key={locationName}>
            <h3 style={{ margin: '0 0 12px', fontSize: '16px', fontWeight: 700, color: '#1a1a2e', padding: '12px 16px', background: '#f0f4f8', borderRadius: '8px', borderLeft: '4px solid #e94560' }}>
              📍 {locationName}
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {locationBookings.map(b => (
                <div key={b.id} style={cardStyle}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, color: '#1a1a2e', marginBottom: '8px' }}>
                      Бронювання #{b.id}
                    </div>
                    <div style={{ background: '#f9f9f9', padding: '10px 12px', borderRadius: '8px', marginBottom: '10px', fontSize: '13px' }}>
                      <div style={{ color: '#1a1a2e', fontWeight: 600, marginBottom: '4px' }}>
                        👤 {b.user_full_name}
                      </div>
                      {b.user_phone && (
                        <div style={{ color: '#666' }}>
                          📱 {b.user_phone}
                        </div>
                      )}
                    </div>
                    <div style={{ color: '#888', fontSize: '13px', marginBottom: '8px' }}>
                      <div>🕐 {new Date(b.start_time).toLocaleString('uk-UA')}</div>
                      <div>💰 {b.total_price}₴</div>
                    </div>
                    {b.notes && (
                      <div style={{ background: '#fff3e0', padding: '10px 12px', borderRadius: '8px', fontSize: '13px', color: '#666', borderLeft: '3px solid #FF9800' }}>
                        <div style={{ fontWeight: 600, color: '#FF9800', marginBottom: '4px' }}>📝 Коментар:</div>
                        {b.notes}
                      </div>
                    )}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '12px', minWidth: '200px' }}>
                    <select value={b.status} onChange={e => handleStatus(b.id, e.target.value)}
                      style={{ ...inputStyle, width: '100%' }}>
                      {Object.entries(STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
                    </select>
                    <button onClick={() => navigate(`/bookings/${b.id}`)} style={{ ...btnGray, width: '100%', textAlign: 'center' }}>
                      Деталі
                    </button>
                    <div style={{ color: '#888', fontSize: '12px' }}>
                      {new Date(b.created_at).toLocaleDateString('uk-UA')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
        {bookings.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#888' }}>
            Немає бронювань
          </div>
        )}
      </div>
    </div>
  );
}
BookingsTab.propTypes = {
  bookings: PropTypes.array.isRequired,
  setBookings: PropTypes.func.isRequired,
};

// ---- USERS TAB ----
function UsersTab({ users, setUsers }) {
  const handleDeactivate = async (id) => {
    if (!globalThis.confirm('Заблокувати користувача?')) return;
    await usersApi.deactivate(id);
    toast.success('Користувача заблоковано');
    usersApi.getAll().then(r => setUsers(r.data));
  };

  return (
    <div>
      <h2 style={{ margin: '0 0 16px', fontSize: '18px', fontWeight: 700 }}>Користувачі ({users.length})</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {users.map(u => (
          <div key={u.id} style={cardStyle}>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700 }}>{u.full_name} <span style={{ color: u.role === 'admin' ? '#e94560' : '#888', fontSize: '12px' }}>({u.role})</span></div>
              <div style={{ color: '#888', fontSize: '13px' }}>{u.email} {u.phone && `· ${u.phone}`}</div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                background: u.is_active ? '#E8F5E9' : '#FFEBEE',
                color: u.is_active ? '#4CAF50' : '#f44336',
                padding: '3px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 700,
              }}>{u.is_active ? 'Активний' : 'Заблокований'}</span>
              {u.is_active && u.role !== 'admin' && (
                <button onClick={() => handleDeactivate(u.id)} style={{ ...btnGray, color: '#f44336' }}>🚫</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
UsersTab.propTypes = {
  users: PropTypes.array.isRequired,
  setUsers: PropTypes.func.isRequired,
};

// Shared styles
const btnRed = { background: '#e94560', color: '#fff', border: 'none', borderRadius: '8px', padding: '8px 16px', cursor: 'pointer', fontWeight: 700, fontSize: '13px' };
const btnGray = { background: '#fff', color: '#555', border: '1.5px solid #e0e0e0', borderRadius: '8px', padding: '7px 14px', cursor: 'pointer', fontWeight: 600, fontSize: '13px' };
const inputStyle = { width: '100%', padding: '8px 12px', border: '1.5px solid #e0e0e0', borderRadius: '8px', fontSize: '13px', outline: 'none', boxSizing: 'border-box' };
const labelStyle = { display: 'block', fontSize: '12px', fontWeight: 600, color: '#666', marginBottom: '4px' };
const cardStyle = { background: '#fff', borderRadius: '12px', padding: '16px 20px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', display: 'flex', alignItems: 'center', gap: '16px' };
const modalOverlay = { position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200 };
const modalBox = { background: '#fff', borderRadius: '20px', padding: '32px', width: '460px', maxHeight: '80vh', overflowY: 'auto' };

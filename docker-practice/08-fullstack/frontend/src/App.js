import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [items, setItems] = useState([]);
  const [name, setName]   = useState('');

  const fetchItems = async () => {
    const res = await fetch(`${API}/items`);
    const data = await res.json();
    setItems(data);
  };

  const addItem = async () => {
    if (!name.trim()) return;
    await fetch(`${API}/items`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    setName('');
    fetchItems();
  };

  const deleteItem = async (id) => {
    await fetch(`${API}/items/${id}`, { method: 'DELETE' });
    fetchItems();
  };

  useEffect(() => { fetchItems(); }, []);

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>🐳 Fullstack Docker App</h1>
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        <input
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Enter item name..."
          style={{ flex: 1, padding: 8, fontSize: 16 }}
        />
        <button onClick={addItem} style={{ padding: '8px 16px' }}>Add</button>
      </div>
      {items.length === 0 && <p>No items yet. Add one above!</p>}
      {items.map(item => (
        <div key={item._id} style={{
          display: 'flex', justifyContent: 'space-between',
          padding: 12, marginBottom: 8,
          background: '#f5f5f5', borderRadius: 6
        }}>
          <span>{item.name}</span>
          <button onClick={() => deleteItem(item._id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}

export default App;
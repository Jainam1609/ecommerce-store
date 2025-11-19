import React, { useState } from 'react';
import './App.css';
import Cart from './components/Cart';
import Admin from './components/Admin';

function App() {
  const [activeTab, setActiveTab] = useState<'cart' | 'admin'>('cart');
  const [userId] = useState('user1'); // In a real app, this would come from auth

  return (
    <div className="container">
      <div className="header">
        <h1>E-commerce Store</h1>
        <p>Add items to your cart and checkout to place an order</p>
      </div>

      <div className="tabs">
        <button
          className={`tab-button ${activeTab === 'cart' ? 'active' : ''}`}
          onClick={() => setActiveTab('cart')}
        >
          Shopping Cart
        </button>
        <button
          className={`tab-button ${activeTab === 'admin' ? 'active' : ''}`}
          onClick={() => setActiveTab('admin')}
        >
          Admin Dashboard
        </button>
      </div>

      {activeTab === 'cart' && <Cart userId={userId} />}
      {activeTab === 'admin' && <Admin />}
    </div>
  );
}

export default App;


import React, { useState, useEffect } from 'react';
import { Statistics, DiscountCode } from '../types';
import { adminApi } from '../api';

const Admin: React.FC = () => {
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    setLoading(true);
    try {
      const stats = await adminApi.getStatistics();
      setStatistics(stats);
    } catch (error) {
      showMessage('error', 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handleGenerateDiscountCode = async () => {
    setLoading(true);
    try {
      const discount = await adminApi.generateDiscountCode();
      showMessage('success', `Discount code generated: ${discount.code}`);
      await loadStatistics();
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to generate discount code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="card">
        <h2>Admin Actions</h2>
        <button
          className="button"
          onClick={handleGenerateDiscountCode}
          disabled={loading}
        >
          Generate Discount Code
        </button>
        <button
          className="button button-secondary"
          onClick={loadStatistics}
          disabled={loading}
        >
          Refresh Statistics
        </button>
      </div>

      {loading && !statistics && (
        <div className="card">
          <p>Loading statistics...</p>
        </div>
      )}

      {statistics && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Items Purchased</h3>
              <div className="value">{statistics.total_items_purchased}</div>
            </div>
            <div className="stat-card">
              <h3>Total Purchase Amount</h3>
              <div className="value">${statistics.total_purchase_amount.toFixed(2)}</div>
            </div>
            <div className="stat-card">
              <h3>Total Discount Amount</h3>
              <div className="value">${statistics.total_discount_amount.toFixed(2)}</div>
            </div>
            <div className="stat-card">
              <h3>Total Orders</h3>
              <div className="value">{statistics.total_orders}</div>
            </div>
          </div>

          <div className="card">
            <h2>Discount Codes</h2>
            {statistics.discount_codes.length === 0 ? (
              <div className="empty-state">
                <p>No discount codes generated yet</p>
              </div>
            ) : (
              <div className="discount-codes-list">
                {statistics.discount_codes.map((code) => (
                  <div
                    key={code.code}
                    className={`discount-code-item ${code.used ? 'used' : ''}`}
                  >
                    <div>
                      <div className="discount-code">{code.code}</div>
                      <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                        Created: {new Date(code.created_at).toLocaleString()}
                        {code.used && code.used_at && (
                          <> • Used: {new Date(code.used_at).toLocaleString()}</>
                        )}
                      </div>
                    </div>
                    <div>
                      {code.used ? (
                        <span style={{ color: '#e74c3c', fontWeight: 'bold' }}>USED</span>
                      ) : (
                        <span style={{ color: '#27ae60', fontWeight: 'bold' }}>AVAILABLE</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Admin;


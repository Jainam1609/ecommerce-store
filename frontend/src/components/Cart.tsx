import React, { useState, useEffect } from 'react';
import { CartItem, Order } from '../types';
import { cartApi, checkoutApi } from '../api';

interface CartProps {
  userId: string;
}

const Cart: React.FC<CartProps> = ({ userId }) => {
  const [cart, setCart] = useState<{ items: CartItem[] }>({ items: [] });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [order, setOrder] = useState<Order | null>(null);
  const [discountCode, setDiscountCode] = useState('');
  
  // Form state
  const [itemId, setItemId] = useState('');
  const [itemName, setItemName] = useState('');
  const [itemPrice, setItemPrice] = useState('');
  const [itemQuantity, setItemQuantity] = useState('1');
  
  // Form validation errors
  const [errors, setErrors] = useState<{
    itemId?: string;
    itemName?: string;
    itemPrice?: string;
    itemQuantity?: string;
    discountCode?: string;
  }>({});

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      const cartData = await cartApi.getCart(userId);
      setCart(cartData);
    } catch (error) {
      showMessage('error', 'Failed to load cart');
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const validateAddItemForm = (): boolean => {
    const newErrors: typeof errors = {};

    // Validate Item ID
    if (!itemId.trim()) {
      newErrors.itemId = 'Item ID is required';
    } else if (itemId.length > 100) {
      newErrors.itemId = 'Item ID must be 100 characters or less';
    }

    // Validate Item Name
    if (!itemName.trim()) {
      newErrors.itemName = 'Item name is required';
    } else if (itemName.length > 200) {
      newErrors.itemName = 'Item name must be 200 characters or less';
    }

    // Validate Price
    if (!itemPrice.trim()) {
      newErrors.itemPrice = 'Price is required';
    } else {
      const price = parseFloat(itemPrice);
      if (isNaN(price)) {
        newErrors.itemPrice = 'Price must be a valid number';
      } else if (price <= 0) {
        newErrors.itemPrice = 'Price must be greater than 0';
      } else if (price > 999999.99) {
        newErrors.itemPrice = 'Price must be less than 1,000,000';
      }
    }

    // Validate Quantity
    if (!itemQuantity.trim()) {
      newErrors.itemQuantity = 'Quantity is required';
    } else {
      const quantity = parseInt(itemQuantity);
      if (isNaN(quantity)) {
        newErrors.itemQuantity = 'Quantity must be a valid number';
      } else if (quantity <= 0) {
        newErrors.itemQuantity = 'Quantity must be greater than 0';
      } else if (quantity > 1000) {
        newErrors.itemQuantity = 'Quantity must be 1000 or less';
      } else if (!Number.isInteger(parseFloat(itemQuantity))) {
        newErrors.itemQuantity = 'Quantity must be a whole number';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateDiscountCode = (code: string): boolean => {
    if (!code.trim()) {
      return true; // Optional field
    }
    // Discount code format: SAVE10-XXXX where XXXX is digits
    const discountCodePattern = /^SAVE10-\d{4}$/;
    return discountCodePattern.test(code.trim());
  };

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Clear previous errors
    setErrors({});
    
    // Validate form
    if (!validateAddItemForm()) {
      showMessage('error', 'Please fix the validation errors');
      return;
    }

    setLoading(true);
    try {
      await cartApi.addItem(
        userId,
        itemId.trim(),
        itemName.trim(),
        parseFloat(itemPrice),
        parseInt(itemQuantity)
      );
      await loadCart();
      setItemId('');
      setItemName('');
      setItemPrice('');
      setItemQuantity('1');
      setErrors({});
      showMessage('success', 'Item added to cart');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Failed to add item');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveItem = async (itemId: string) => {
    setLoading(true);
    try {
      await cartApi.removeItem(userId, itemId);
      await loadCart();
      showMessage('success', 'Item removed from cart');
    } catch (error) {
      showMessage('error', 'Failed to remove item');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async () => {
    if (cart.items.length === 0) {
      showMessage('error', 'Cart is empty');
      return;
    }

    // Validate discount code if provided
    if (discountCode.trim() && !validateDiscountCode(discountCode)) {
      setErrors({ discountCode: 'Invalid discount code format. Expected: SAVE10-XXXX' });
      showMessage('error', 'Invalid discount code format');
      return;
    }

    setLoading(true);
    setErrors({});
    try {
      const orderData = await checkoutApi.checkout(
        userId,
        discountCode.trim() || undefined
      );
      setOrder(orderData);
      setCart({ items: [] });
      setDiscountCode('');
      showMessage('success', 'Order placed successfully!');
    } catch (error: any) {
      showMessage('error', error.response?.data?.detail || 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  const calculateSubtotal = () => {
    return cart.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  };

  const subtotal = calculateSubtotal();
  const discountAmount = discountCode ? subtotal * 0.1 : 0;
  const total = subtotal - discountAmount;

  return (
    <div>
      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="card">
        <h2>Add Item to Cart</h2>
        <form onSubmit={handleAddItem}>
          <div className="form-group">
            <label>Item ID *</label>
            <input
              type="text"
              value={itemId}
              onChange={(e) => {
                setItemId(e.target.value);
                if (errors.itemId) {
                  setErrors({ ...errors, itemId: undefined });
                }
              }}
              placeholder="e.g., item1"
              required
              maxLength={100}
              className={errors.itemId ? 'error' : ''}
            />
            {errors.itemId && <span className="error-message">{errors.itemId}</span>}
          </div>
          <div className="form-group">
            <label>Item Name *</label>
            <input
              type="text"
              value={itemName}
              onChange={(e) => {
                setItemName(e.target.value);
                if (errors.itemName) {
                  setErrors({ ...errors, itemName: undefined });
                }
              }}
              placeholder="e.g., Product Name"
              required
              maxLength={200}
              className={errors.itemName ? 'error' : ''}
            />
            {errors.itemName && <span className="error-message">{errors.itemName}</span>}
          </div>
          <div className="form-group">
            <label>Price *</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              max="999999.99"
              value={itemPrice}
              onChange={(e) => {
                setItemPrice(e.target.value);
                if (errors.itemPrice) {
                  setErrors({ ...errors, itemPrice: undefined });
                }
              }}
              placeholder="e.g., 10.99"
              required
              className={errors.itemPrice ? 'error' : ''}
            />
            {errors.itemPrice && <span className="error-message">{errors.itemPrice}</span>}
          </div>
          <div className="form-group">
            <label>Quantity *</label>
            <input
              type="number"
              min="1"
              max="1000"
              step="1"
              value={itemQuantity}
              onChange={(e) => {
                setItemQuantity(e.target.value);
                if (errors.itemQuantity) {
                  setErrors({ ...errors, itemQuantity: undefined });
                }
              }}
              required
              className={errors.itemQuantity ? 'error' : ''}
            />
            {errors.itemQuantity && <span className="error-message">{errors.itemQuantity}</span>}
          </div>
          <button type="submit" className="button" disabled={loading}>
            Add to Cart
          </button>
        </form>
      </div>

      <div className="card">
        <h2>Your Cart</h2>
        {cart.items.length === 0 ? (
          <div className="empty-state">
            <p>Your cart is empty</p>
          </div>
        ) : (
          <>
            {cart.items.map((item) => (
              <div key={item.item_id} className="cart-item">
                <div className="cart-item-info">
                  <div className="cart-item-name">{item.name}</div>
                  <div className="cart-item-details">
                    ${item.price.toFixed(2)} × {item.quantity} = ${(item.price * item.quantity).toFixed(2)}
                  </div>
                </div>
                <div className="cart-item-actions">
                  <button
                    className="button button-danger"
                    onClick={() => handleRemoveItem(item.item_id)}
                    disabled={loading}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}

            <div className="cart-summary">
              <div className="cart-summary-row">
                <span>Subtotal:</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              {discountAmount > 0 && (
                <>
                  <div className="cart-summary-row">
                    <span>Discount (10%):</span>
                    <span>-${discountAmount.toFixed(2)}</span>
                  </div>
                </>
              )}
              <div className="cart-summary-row total">
                <span>Total:</span>
                <span>${total.toFixed(2)}</span>
              </div>

              <div className="discount-input">
                <input
                  type="text"
                  value={discountCode}
                  onChange={(e) => {
                    setDiscountCode(e.target.value);
                    if (errors.discountCode) {
                      setErrors({ ...errors, discountCode: undefined });
                    }
                  }}
                  placeholder="Enter discount code (e.g., SAVE10-0001)"
                  maxLength={50}
                  className={errors.discountCode ? 'error' : ''}
                />
                {errors.discountCode && (
                  <span className="error-message" style={{ display: 'block', marginTop: '5px' }}>
                    {errors.discountCode}
                  </span>
                )}
              </div>

              <button
                className="button"
                onClick={handleCheckout}
                disabled={loading}
                style={{ marginTop: '15px', width: '100%' }}
              >
                {loading ? 'Processing...' : 'Checkout'}
              </button>
            </div>
          </>
        )}
      </div>

      {order && (
        <div className="card">
          <h2>Order Confirmation</h2>
          <div className="order-details">
            <h3>Order ID: {order.order_id}</h3>
            <p><strong>Date:</strong> {new Date(order.created_at).toLocaleString()}</p>
            <div style={{ marginTop: '15px' }}>
              <strong>Items:</strong>
              {order.items.map((item: any, index: number) => (
                <div key={index} className="order-item">
                  {item.name} - ${item.price.toFixed(2)} × {item.quantity}
                </div>
              ))}
            </div>
            <div style={{ marginTop: '15px' }}>
              <p><strong>Subtotal:</strong> ${order.subtotal.toFixed(2)}</p>
              {order.discount_code && (
                <p><strong>Discount Code:</strong> {order.discount_code}</p>
              )}
              {order.discount_amount > 0 && (
                <p><strong>Discount:</strong> -${order.discount_amount.toFixed(2)}</p>
              )}
              <p><strong>Total:</strong> ${order.total.toFixed(2)}</p>
            </div>
          </div>
          <button
            className="button button-secondary"
            onClick={() => setOrder(null)}
            style={{ marginTop: '15px' }}
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
};

export default Cart;


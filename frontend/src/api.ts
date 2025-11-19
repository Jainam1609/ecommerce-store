import axios from 'axios';
import { Cart, CartItem, Order, DiscountCode, Statistics } from './types';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Cart API
export const cartApi = {
  getCart: async (userId: string): Promise<Cart> => {
    const response = await api.get(`/api/cart/${userId}`);
    return response.data;
  },

  addItem: async (
    userId: string,
    itemId: string,
    name: string,
    price: number,
    quantity: number
  ): Promise<Cart> => {
    const response = await api.post(`/api/cart/${userId}/add`, {
      item_id: itemId,
      name,
      price,
      quantity,
    });
    return response.data;
  },

  removeItem: async (userId: string, itemId: string): Promise<Cart> => {
    const response = await api.delete(`/api/cart/${userId}/item/${itemId}`);
    return response.data;
  },

  clearCart: async (userId: string): Promise<void> => {
    await api.delete(`/api/cart/${userId}/clear`);
  },
};

// Checkout API
export const checkoutApi = {
  checkout: async (userId: string, discountCode?: string): Promise<Order> => {
    const response = await api.post(`/api/checkout/${userId}`, {
      discount_code: discountCode || null,
    });
    return response.data;
  },
};

// Admin API
export const adminApi = {
  generateDiscountCode: async (): Promise<DiscountCode> => {
    const response = await api.post('/api/admin/discount-code/generate');
    return response.data;
  },

  getStatistics: async (): Promise<Statistics> => {
    const response = await api.get('/api/admin/statistics');
    return response.data;
  },
};


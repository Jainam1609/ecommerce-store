export interface CartItem {
  item_id: string;
  name: string;
  price: number;
  quantity: number;
}

export interface Cart {
  user_id: string;
  items: CartItem[];
}

export interface Order {
  order_id: string;
  user_id: string;
  items: CartItem[];
  subtotal: number;
  discount_code: string | null;
  discount_amount: number;
  total: number;
  created_at: string;
}

export interface DiscountCode {
  code: string;
  discount_percent: number;
  created_at: string;
  used: boolean;
  used_at: string | null;
}

export interface Statistics {
  total_items_purchased: number;
  total_purchase_amount: number;
  total_discount_amount: number;
  discount_codes: DiscountCode[];
  total_orders: number;
}


"""
Store for the e-commerce application
Manages carts, orders, discount codes, and statistics
Uses JSON file-based persistence for data durability
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from app.models import Cart, CartItem, Order, DiscountCode

class Store:
    """
    Store for managing e-commerce data with JSON file-based persistence
    
    Data is maintained in memory during runtime and automatically persisted
    to a JSON file for durability across server restarts.
    """
    def __init__(self, n: int = 5, data_file: str = "data/store.json"):
        """
        Initialize the store
        
        Args:
            n: Every nth order gets a discount code (default: 5)
            data_file: Path to JSON file for persistence (default: "data/store.json")
        """
        self.n = n  # Every nth order gets a discount code
        self.data_file = data_file
        self.carts: Dict[str, Cart] = {}  # user_id -> Cart
        self.orders: List[Order] = []
        self.discount_codes: List[DiscountCode] = []
        self.order_count = 0
        
        # Load data from file if it exists
        self._load_data()
    
    def get_or_create_cart(self, user_id: str) -> Cart:
        """
        Get existing cart or create a new one for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Cart object for the user
        """
        if user_id not in self.carts:
            self.carts[user_id] = Cart(user_id=user_id, items=[])
        return self.carts[user_id]
    
    def add_item_to_cart(self, user_id: str, item_id: str, name: str, price: float, quantity: int) -> Cart:
        """
        Add an item to the user's cart
        
        Args:
            user_id: Unique identifier for the user
            item_id: Unique identifier for the item
            name: Name of the item
            price: Price per unit
            quantity: Quantity to add
            
        Returns:
            Updated Cart object
        """
        cart = self.get_or_create_cart(user_id)
        
        # Check if item already exists in cart
        for cart_item in cart.items:
            if cart_item.item_id == item_id:
                cart_item.quantity += quantity
                # Persist data
                self._save_data()
                return cart
        
        # Add new item to cart
        cart.items.append(CartItem(
            item_id=item_id,
            name=name,
            price=price,
            quantity=quantity
        ))
        
        # Persist data
        self._save_data()
        
        return cart
    
    def remove_item_from_cart(self, user_id: str, item_id: str) -> Optional[Cart]:
        """
        Remove an item from the user's cart
        
        Args:
            user_id: Unique identifier for the user
            item_id: Unique identifier for the item
            
        Returns:
            Updated Cart object or None if cart doesn't exist
        """
        if user_id not in self.carts:
            return None
        
        cart = self.carts[user_id]
        cart.items = [item for item in cart.items if item.item_id != item_id]
        
        # Persist data
        self._save_data()
        
        return cart
    
    def get_cart(self, user_id: str) -> Optional[Cart]:
        """
        Get the cart for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Cart object or None if cart doesn't exist
        """
        return self.carts.get(user_id)
    
    def clear_cart(self, user_id: str) -> None:
        """
        Clear the cart for a user
        
        Args:
            user_id: Unique identifier for the user
        """
        if user_id in self.carts:
            del self.carts[user_id]
            # Persist data
            self._save_data()
    
    def create_order(self, user_id: str, discount_code: Optional[str] = None) -> Order:
        """
        Create an order from the user's cart
        
        Args:
            user_id: Unique identifier for the user
            discount_code: Optional discount code to apply
            
        Returns:
            Created Order object
        """
        cart = self.get_cart(user_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty")
        
        # Calculate subtotal
        subtotal = sum(item.price * item.quantity for item in cart.items)
        
        # Validate and apply discount code
        discount_amount = 0.0
        applied_discount_code = None
        
        if discount_code:
            discount = self.validate_discount_code(discount_code)
            if discount and self.order_count % self.n == 0:
                discount_amount = subtotal * 0.10  # 10% discount
                applied_discount_code = discount_code
                discount.used = True
                discount.used_at = datetime.now()
            elif discount and self.order_count % self.n != 0:
                raise ValueError(f"Discount code can only be used on every {self.n}th order")
            else:
                raise ValueError("Invalid or already used discount code")
        
        total = subtotal - discount_amount
        
        # Create order
        order = Order(
            order_id=f"ORD-{len(self.orders) + 1:06d}",
            user_id=user_id,
            items=[item.model_dump() for item in cart.items],
            subtotal=subtotal,
            discount_code=applied_discount_code,
            discount_amount=discount_amount,
            total=total,
            created_at=datetime.now()
        )
        
        self.orders.append(order)
        self.order_count += 1
        
        # Check if this is the nth order and generate discount code
        if self.order_count % self.n == 0:
            self.generate_discount_code()
        
        # Clear cart after order
        self.clear_cart(user_id)
        
        # Persist data (order and discount code changes)
        self._save_data()
        
        return order
    
    def validate_discount_code(self, code: str) -> Optional[DiscountCode]:
        """
        Validate if a discount code is valid and available
        
        Args:
            code: Discount code to validate
            
        Returns:
            DiscountCode object if valid, None otherwise
        """
        for discount in self.discount_codes:
            if discount.code == code and not discount.used:
                return discount
        return None
    
    def generate_discount_code(self) -> DiscountCode:
        """
        Generate a new discount code (called every nth order)
        
        Returns:
            Created DiscountCode object
        """
        code = f"SAVE10-{len(self.discount_codes) + 1:04d}"
        discount = DiscountCode(
            code=code,
            discount_percent=10,
            created_at=datetime.now(),
            used=False
        )
        self.discount_codes.append(discount)
        
        # Persist data
        self._save_data()
        
        return discount
    
    def get_statistics(self) -> Dict:
        """
        Get store statistics for admin
        
        Returns:
            Dictionary containing statistics
        """
        total_items_purchased = sum(
            sum(item['quantity'] for item in order.items)
            for order in self.orders
        )
        
        total_purchase_amount = sum(order.total for order in self.orders)
        
        total_discount_amount = sum(order.discount_amount for order in self.orders)
        
        discount_codes_list = [
            {
                "code": dc.code,
                "created_at": dc.created_at.isoformat(),
                "used": dc.used,
                "used_at": dc.used_at.isoformat() if dc.used_at else None
            }
            for dc in self.discount_codes
        ]
        
        return {
            "total_items_purchased": total_items_purchased,
            "total_purchase_amount": round(total_purchase_amount, 2),
            "total_discount_amount": round(total_discount_amount, 2),
            "discount_codes": discount_codes_list,
            "total_orders": len(self.orders)
        }
    
    def _load_data(self) -> None:
        """
        Load data from JSON file if it exists
        """
        try:
            data_path = Path(self.data_file)
            if data_path.exists():
                with open(data_path, 'r') as f:
                    data = json.load(f)
                
                # Load carts
                self.carts = {}
                for user_id, cart_data in data.get('carts', {}).items():
                    items = [CartItem(**item) for item in cart_data.get('items', [])]
                    self.carts[user_id] = Cart(user_id=user_id, items=items)
                
                # Load orders
                self.orders = []
                for order_data in data.get('orders', []):
                    # Convert datetime strings back to datetime objects
                    order_data['created_at'] = datetime.fromisoformat(order_data['created_at'])
                    self.orders.append(Order(**order_data))
                
                # Load discount codes
                self.discount_codes = []
                for dc_data in data.get('discount_codes', []):
                    dc_data['created_at'] = datetime.fromisoformat(dc_data['created_at'])
                    if dc_data.get('used_at'):
                        dc_data['used_at'] = datetime.fromisoformat(dc_data['used_at'])
                    self.discount_codes.append(DiscountCode(**dc_data))
                
                # Load order count
                self.order_count = data.get('order_count', len(self.orders))
                self.n = data.get('n', self.n)
                
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            # If file doesn't exist or is corrupted, start fresh
            print(f"Could not load data from {self.data_file}: {e}. Starting with empty store.")
            self.carts = {}
            self.orders = []
            self.discount_codes = []
            self.order_count = 0
    
    def _save_data(self) -> None:
        """
        Save current state to JSON file
        """
        try:
            data_path = Path(self.data_file)
            # Create directory if it doesn't exist
            data_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for serialization
            data = {
                'n': self.n,
                'order_count': self.order_count,
                'carts': {
                    user_id: {
                        'user_id': cart.user_id,
                        'items': [item.model_dump() for item in cart.items]
                    }
                    for user_id, cart in self.carts.items()
                },
                'orders': [
                    {
                        'order_id': order.order_id,
                        'user_id': order.user_id,
                        'items': order.items,
                        'subtotal': order.subtotal,
                        'discount_code': order.discount_code,
                        'discount_amount': order.discount_amount,
                        'total': order.total,
                        'created_at': order.created_at.isoformat()
                    }
                    for order in self.orders
                ],
                'discount_codes': [
                    {
                        'code': dc.code,
                        'discount_percent': dc.discount_percent,
                        'created_at': dc.created_at.isoformat(),
                        'used': dc.used,
                        'used_at': dc.used_at.isoformat() if dc.used_at else None
                    }
                    for dc in self.discount_codes
                ]
            }
            
            # Write to file atomically (write to temp file, then rename)
            temp_file = str(data_path) + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Atomic rename
            os.replace(temp_file, data_path)
            
        except Exception as e:
            print(f"Error saving data to {self.data_file}: {e}")
            # Don't raise - allow operations to continue even if save fails


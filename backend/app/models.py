"""
Data models for the e-commerce application
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CartItem(BaseModel):
    """Represents an item in the cart"""
    item_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    price: float = Field(gt=0, le=999999.99, description="Price must be greater than 0")
    quantity: int = Field(gt=0, le=1000, description="Quantity must be between 1 and 1000")

class Cart(BaseModel):
    """Represents a shopping cart"""
    user_id: str
    items: List[CartItem] = []

class Order(BaseModel):
    """Represents an order"""
    order_id: str
    user_id: str
    items: List[dict]  # List of order items
    subtotal: float
    discount_code: Optional[str] = None
    discount_amount: float = 0.0
    total: float
    created_at: datetime

class DiscountCode(BaseModel):
    """Represents a discount code"""
    code: str
    discount_percent: int = 10
    created_at: datetime
    used: bool = False
    used_at: Optional[datetime] = None

# Request/Response models for API
class AddItemRequest(BaseModel):
    """Request model for adding item to cart"""
    item_id: str = Field(
        min_length=1,
        max_length=100,
        description="Item identifier (1-100 characters)"
    )
    name: str = Field(
        min_length=1,
        max_length=200,
        description="Item name (1-200 characters)"
    )
    price: float = Field(
        gt=0,
        le=999999.99,
        description="Price per unit (must be greater than 0 and less than 1,000,000)"
    )
    quantity: int = Field(
        gt=0,
        le=1000,
        default=1,
        description="Quantity (must be between 1 and 1000)"
    )

class CheckoutRequest(BaseModel):
    """Request model for checkout"""
    discount_code: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Optional discount code (format: SAVE10-XXXX)"
    )

class CheckoutResponse(BaseModel):
    """Response model for checkout"""
    order_id: str
    user_id: str
    items: List[dict]
    subtotal: float
    discount_code: Optional[str] = None
    discount_amount: float
    total: float
    created_at: str


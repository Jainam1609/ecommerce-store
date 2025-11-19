"""
Cart API endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from app.models import AddItemRequest, Cart
from app.store import Store

router = APIRouter()

def get_store(request: Request) -> Store:
    """Get the store instance from app state"""
    return request.app.state.store

@router.post("/{user_id}/add", response_model=Cart, summary="Add item to cart")
def add_item_to_cart(user_id: str, item: AddItemRequest, request: Request):
    """
    Add an item to the user's cart.
    
    If the item already exists in the cart, the quantity will be incremented.
    Otherwise, a new item will be added to the cart.
    
    **Example Request:**
    ```json
    {
        "item_id": "item1",
        "name": "Laptop",
        "price": 999.99,
        "quantity": 1
    }
    ```
    
    Args:
        user_id: Unique identifier for the user
        item: Item details to add to cart
        
    Returns:
        Updated cart with the new item added
    """
    store = get_store(request)
    try:
        cart = store.add_item_to_cart(
            user_id=user_id,
            item_id=item.item_id,
            name=item.name,
            price=item.price,
            quantity=item.quantity
        )
        return cart
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=Cart, summary="Get user's cart")
def get_cart(user_id: str, request: Request):
    """
    Retrieve the user's shopping cart.
    
    If the user doesn't have a cart, returns an empty cart.
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        User's cart with all items
    """
    store = get_store(request)
    cart = store.get_cart(user_id)
    if not cart:
        # Return empty cart if none exists
        return Cart(user_id=user_id, items=[])
    return cart

@router.delete("/{user_id}/item/{item_id}", response_model=Cart)
def remove_item_from_cart(user_id: str, item_id: str, request: Request):
    """
    Remove an item from the user's cart
    
    Args:
        user_id: Unique identifier for the user
        item_id: Unique identifier for the item to remove
        
    Returns:
        Updated cart
    """
    store = get_store(request)
    cart = store.remove_item_from_cart(user_id, item_id)
    if cart is None:
        return Cart(user_id=user_id, items=[])
    return cart

@router.delete("/{user_id}/clear")
def clear_cart(user_id: str, request: Request):
    """
    Clear the user's cart
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        Success message
    """
    store = get_store(request)
    store.clear_cart(user_id)
    return {"message": "Cart cleared successfully"}


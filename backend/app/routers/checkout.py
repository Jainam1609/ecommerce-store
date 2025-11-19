"""
Checkout API endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from app.models import CheckoutRequest, CheckoutResponse
from app.store import Store

router = APIRouter()

def get_store(request: Request) -> Store:
    """Get the store instance from app state"""
    return request.app.state.store

@router.post("/{user_id}", response_model=CheckoutResponse, summary="Process checkout")
def checkout(user_id: str, checkout_request: CheckoutRequest, request: Request):
    """
    Process checkout for the user's cart.
    
    Creates an order from the items in the cart. If a discount code is provided,
    it will be validated and applied (10% discount). The cart will be cleared
    after successful checkout.
    
    **Discount Code System:**
    - Every 5th order automatically generates a new discount code
    - Discount codes can only be used once
    - Discount applies to the entire order (10% off)
    
    **Example Request (with discount):**
    ```json
    {
        "discount_code": "SAVE10-0001"
    }
    ```
    
    **Example Request (without discount):**
    ```json
    {}
    ```
    
    Args:
        user_id: Unique identifier for the user
        checkout_request: Checkout details including optional discount code
        
    Returns:
        Order details including order_id, items, totals, and discount information
        
    Raises:
        HTTPException 400: If cart is empty or discount code is invalid/already used
    """
    store = get_store(request)
    
    try:
        order = store.create_order(
            user_id=user_id,
            discount_code=checkout_request.discount_code
        )
        
        return CheckoutResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            items=order.items,
            subtotal=order.subtotal,
            discount_code=order.discount_code,
            discount_amount=order.discount_amount,
            total=order.total,
            created_at=order.created_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


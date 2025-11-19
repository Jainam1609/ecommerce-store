"""
Admin API endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from app.models import DiscountCode
from app.store import Store

router = APIRouter()

def get_store(request: Request) -> Store:
    """Get the store instance from app state"""
    return request.app.state.store

@router.post("/discount-code/generate", response_model=DiscountCode, summary="Generate discount code")
def generate_discount_code(request: Request):
    """
    Manually generate a new discount code.
    
    **Note:** Discount codes are automatically generated every 5th order.
    This endpoint allows admins to manually generate codes if needed.
    
    **Generated Code Format:**
    - Pattern: `SAVE10-XXXX` where XXXX is a sequential number
    - Discount: 10% off entire order
    - Single use only
    
    Returns:
        Generated discount code with creation timestamp
    """
    store = get_store(request)
    try:
        discount = store.generate_discount_code()
        return discount
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", summary="Get store statistics")
def get_statistics(request: Request):
    """
    Retrieve comprehensive store statistics.
    
    Returns aggregated data including:
    - Total items purchased across all orders
    - Total revenue (sum of all order totals)
    - Total discount amount given
    - List of all discount codes with usage status
    - Total number of orders placed
    
    **Example Response:**
    ```json
    {
        "total_items_purchased": 15,
        "total_purchase_amount": 1500.00,
        "total_discount_amount": 150.00,
        "discount_codes": [
            {
                "code": "SAVE10-0001",
                "created_at": "2024-01-15T10:00:00",
                "used": true,
                "used_at": "2024-01-15T10:30:00"
            }
        ],
        "total_orders": 5
    }
    ```
    
    Returns:
        Dictionary containing all store statistics
    """
    store = get_store(request)
    try:
        stats = store.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


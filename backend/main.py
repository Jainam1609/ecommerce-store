"""
E-commerce Store Backend API
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import cart, checkout, admin
from app.store import Store

# Initialize FastAPI app with enhanced Swagger documentation
app = FastAPI(
    title="E-commerce Store API",
    version="1.0.0",
    description="""
    ## E-commerce Store Backend API
    
    A comprehensive REST API for managing an e-commerce store with the following features:
    
    ### Features
    * **Cart Management**: Add, remove, and manage items in shopping carts
    * **Checkout**: Process orders with optional discount code validation
    * **Discount System**: Automatic discount code generation every nth order (default: 5th order)
    * **Admin Dashboard**: View statistics and manage discount codes
    
    ### Discount Code System
    * Discount codes are automatically generated every 5th order
    * Each discount code provides 10% off the entire order
    * Discount codes can only be used once
    * Format: `SAVE10-XXXX` where XXXX is a sequential number
    
    ### API Endpoints
    
    #### Cart Endpoints
    * `POST /api/cart/{user_id}/add` - Add item to cart
    * `GET /api/cart/{user_id}` - Get user's cart
    * `DELETE /api/cart/{user_id}/item/{item_id}` - Remove item from cart
    * `DELETE /api/cart/{user_id}/clear` - Clear entire cart
    
    #### Checkout Endpoints
    * `POST /api/checkout/{user_id}` - Process checkout (with optional discount code)
    
    #### Admin Endpoints
    * `POST /api/admin/discount-code/generate` - Manually generate discount code
    * `GET /api/admin/statistics` - Get store statistics
    
    ### Notes
    * All data is persisted to `data/store.json` (automatically created)
    * Data persists across server restarts
    * Use Swagger UI at `/docs` for interactive API testing
    """,
    contact={
        "name": "E-commerce Store API Support",
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {
            "name": "cart",
            "description": "Shopping cart operations. Add, remove, and manage items in user carts.",
        },
        {
            "name": "checkout",
            "description": "Order processing and checkout. Includes discount code validation.",
        },
        {
            "name": "admin",
            "description": "Administrative operations. Generate discount codes and view store statistics.",
        },
    ],
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize store with file-based persistence
store = Store()

# Include routers
app.include_router(cart.router, prefix="/api/cart", tags=["cart"])
app.include_router(checkout.router, prefix="/api/checkout", tags=["checkout"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# Make store available to routers
app.state.store = store

@app.get("/")
def root():
    """Health check endpoint"""
    return {"message": "E-commerce Store API is running"}


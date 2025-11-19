# Quick Start Guide

## Prerequisites
- Python 3.8+ (Python 3.13 recommended)
- Node.js 14+ and npm

## Backend (Terminal 1)

```bash
cd backend

# Create virtual environment (venv)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Upgrade pip (recommended)
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

**Backend URLs:**
- API: http://localhost:8000
- **Swagger UI (Interactive Docs)**: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

**Note**: Always activate your virtual environment (`source venv/bin/activate`) before running commands!

**Data Persistence**: All data (carts, orders, discount codes) is automatically saved to `backend/data/store.json` and persists across server restarts.

## Frontend (Terminal 2)

```bash
cd frontend
npm install
npm start
```

Frontend will run at: http://localhost:3000

## Testing

```bash
cd backend
source venv/bin/activate  # Activate venv first!
pytest
```

## Using Swagger UI

The easiest way to test the API is using Swagger UI:

1. Start the backend server (see above)
2. Open http://localhost:8000/docs in your browser
3. Click on any endpoint to expand it
4. Click "Try it out"
5. Fill in the parameters/body
6. Click "Execute"
7. See the response below

**Example: Testing Add Item to Cart**
1. Go to `POST /api/cart/{user_id}/add`
2. Click "Try it out"
3. Enter `user_id`: `user1`
4. In the request body, enter:
   ```json
   {
     "item_id": "item1",
     "name": "Laptop",
     "price": 999.99,
     "quantity": 1
   }
   ```
5. Click "Execute"
6. See the response with the updated cart

## Example Usage

### 1. Add items to cart via UI
- Go to "Shopping Cart" tab
- Fill in item details and click "Add to Cart"

### 2. Checkout
- Enter discount code (if available)
- Click "Checkout"

### 3. View Admin Statistics
- Go to "Admin Dashboard" tab
- View statistics and discount codes
- Generate discount codes manually if needed

### 4. Test Discount Code System
- Place 5 orders (default n=5)
- After the 5th order, a discount code will be automatically generated
- Use the discount code in the next checkout

## API Examples (using curl)

### Add item to cart
```bash
curl -X POST "http://localhost:8000/api/cart/user1/add" \
  -H "Content-Type: application/json" \
  -d '{"item_id": "item1", "name": "Product 1", "price": 10.0, "quantity": 2}'
```

### Get cart
```bash
curl "http://localhost:8000/api/cart/user1"
```

### Checkout
```bash
curl -X POST "http://localhost:8000/api/checkout/user1" \
  -H "Content-Type: application/json" \
  -d '{"discount_code": "SAVE10-0001"}'
```

### Get statistics
```bash
curl "http://localhost:8000/api/admin/statistics"
```


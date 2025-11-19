# E-commerce Store

A full-stack e-commerce application with cart management, checkout functionality, and discount code system. Built with Python (FastAPI) backend and React TypeScript frontend.

## Features

- **Cart Management**: Add, remove, and view items in shopping cart
- **Checkout**: Process orders with optional discount code validation
- **Discount System**: Every nth order automatically generates a 10% discount code
- **Admin Dashboard**: View statistics and manage discount codes
- **Data Persistence**: JSON file-based storage - data persists across server restarts

## Project Structure

```
E-commerce store/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── models.py    # Data models
│   │   ├── store.py     # Store logic with file-based persistence
│   │   └── routers/     # API route handlers
│   ├── tests/           # Unit tests
│   ├── main.py          # Application entry point
│   └── requirements.txt # Python dependencies
├── frontend/            # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── api.ts       # API client
│   │   └── types.ts     # TypeScript types
│   └── package.json     # Node dependencies
└── README.md
```

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 14 or higher and npm** - [Download Node.js](https://nodejs.org/)
- **Git** (optional, for version control)

## Setup Instructions

### Backend Setup

1. **Navigate to the backend directory:**
```bash
cd backend
```

2. **Create a virtual environment (highly recommended):**
```bash
# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
```

3. **Upgrade pip (recommended):**
```bash
pip install --upgrade pip
```

4. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**Note**: The requirements.txt uses version ranges (e.g., `>=`) to ensure compatibility with Python 3.13 and newer versions of dependencies. The installed versions will be:
- FastAPI >= 0.104.1
- Uvicorn[standard] >= 0.24.0 (includes additional performance features)
- Pydantic >= 2.9.0 (compatible with Python 3.13)
- Pytest >= 7.4.3
- And other testing/HTTP dependencies

5. **Verify installation:**
```bash
python -c "import fastapi; print('FastAPI installed successfully')"
```

### Frontend Setup

1. **Navigate to the frontend directory:**
```bash
cd frontend
```

2. **Install Node.js dependencies:**
```bash
npm install
```

If you encounter permission issues, you may need to use:
```bash
npm install --legacy-peer-deps
```

3. **Verify installation:**
```bash
npm list react
```

## How to Run

### Running the Backend Server

1. **Activate your virtual environment** (if not already activated):
```bash
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

2. **Start the FastAPI server:**
```bash
uvicorn main:app --reload --port 8000
```

The `--reload` flag enables auto-reload on code changes (useful for development).

3. **Verify the server is running:**
- Open your browser and navigate to: `http://localhost:8000`
- You should see: `{"message":"E-commerce Store API is running"}`

4. **Access API Documentation (Swagger UI):**
- **Swagger UI**: `http://localhost:8000/docs` - Interactive API documentation where you can test all endpoints
- **ReDoc**: `http://localhost:8000/redoc` - Alternative API documentation format
- **OpenAPI JSON**: `http://localhost:8000/openapi.json` - Raw OpenAPI schema

**Swagger UI Features:**
- Test all API endpoints directly from the browser
- View request/response schemas
- See example requests and responses
- No need for Postman or other API clients for basic testing

### Running the Frontend

1. **Open a new terminal window** (keep the backend server running in the first terminal)

2. **Navigate to the frontend directory:**
```bash
cd frontend
```

3. **Start the React development server:**
```bash
npm start
```

The frontend will automatically open in your browser at `http://localhost:3000`

If the browser doesn't open automatically, manually navigate to `http://localhost:3000`

### Running Tests

1. **Navigate to the backend directory:**
```bash
cd backend
```

2. **Activate virtual environment** (if not already activated):
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

3. **Run all tests:**
```bash
pytest
```

4. **Run tests with verbose output:**
```bash
pytest -v
```

5. **Run a specific test file:**
```bash
pytest tests/test_store.py
pytest tests/test_api.py
```

6. **Run tests with coverage:**
```bash
pytest --cov=app --cov-report=html
```

## Troubleshooting

### Backend Issues

**Issue: `uvicorn: command not found`**
- Solution: Make sure your virtual environment is activated and dependencies are installed
- Try: `pip install uvicorn[standard]`

**Issue: Port 8000 already in use**
- Solution: Use a different port: `uvicorn main:app --reload --port 8001`
- Or kill the process using port 8000

**Issue: Import errors**
- Solution: Make sure you're in the backend directory and virtual environment is activated
- Verify: `python -c "from app.store import Store"`

### Frontend Issues

**Issue: `npm: command not found`**
- Solution: Install Node.js from [nodejs.org](https://nodejs.org/)

**Issue: Port 3000 already in use**
- Solution: The React app will prompt you to use a different port (usually 3001)
- Or manually specify: `PORT=3001 npm start`

**Issue: Cannot connect to backend API**
- Solution: Ensure the backend server is running on `http://localhost:8000`
- Check CORS settings in `backend/main.py` if using a different frontend port

**Issue: Module not found errors**
- Solution: Delete `node_modules` and `package-lock.json`, then run `npm install` again

## Development Workflow

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --port 8000
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm start
   ```

3. **Make changes** to the code - both servers will auto-reload

4. **Test your changes** in the browser at `http://localhost:3000`

5. **Run tests** before committing:
   ```bash
   cd backend
   pytest
   ```

## API Documentation

### Swagger UI (Interactive API Documentation)

FastAPI automatically generates interactive API documentation using Swagger UI. This is the easiest way to test and explore the API.

**Access Swagger UI:**
- URL: `http://localhost:8000/docs`
- Available once the backend server is running

**Features:**
- **Try it out**: Test any endpoint directly from the browser
- **Request/Response Schemas**: See the exact structure of requests and responses
- **Example Values**: Pre-filled example data for testing
- **Response Codes**: See all possible response codes for each endpoint
- **Authentication**: (Not required for this API)

**How to Use:**
1. Start the backend server: `uvicorn main:app --reload --port 8000`
2. Open `http://localhost:8000/docs` in your browser
3. Click on any endpoint to expand it
4. Click "Try it out" to test the endpoint
5. Fill in the required parameters and request body
6. Click "Execute" to send the request
7. View the response below

**Alternative Documentation:**
- **ReDoc**: `http://localhost:8000/redoc` - Clean, readable documentation format
- **OpenAPI JSON**: `http://localhost:8000/openapi.json` - Raw OpenAPI schema for integration with other tools

### API Endpoints Reference

### Cart Endpoints

#### Add Item to Cart
```
POST /api/cart/{user_id}/add
Body: {
  "item_id": "string",
  "name": "string",
  "price": number,
  "quantity": number
}
```

#### Get Cart
```
GET /api/cart/{user_id}
```

#### Remove Item from Cart
```
DELETE /api/cart/{user_id}/item/{item_id}
```

#### Clear Cart
```
DELETE /api/cart/{user_id}/clear
```

### Checkout Endpoints

#### Checkout
```
POST /api/checkout/{user_id}
Body: {
  "discount_code": "string" (optional)
}
```

**Note**: Every nth order (default: 5th) automatically generates a new discount code. The discount code can only be used once before the next one becomes available.

### Admin Endpoints

#### Generate Discount Code
```
POST /api/admin/discount-code/generate
```

#### Get Statistics
```
GET /api/admin/statistics
```

Returns:
- `total_items_purchased`: Total count of items purchased
- `total_purchase_amount`: Total revenue
- `total_discount_amount`: Total discount given
- `discount_codes`: List of all discount codes with usage status
- `total_orders`: Total number of orders

## Discount Code System

- **Generation**: Discount codes are automatically generated every nth order (default: every 5th order)
- **Usage**: Each discount code can only be used once
- **Discount**: 10% off the entire order
- **Format**: Codes follow the pattern `SAVE10-XXXX` where XXXX is a sequential number

## Data Persistence

The application uses **JSON file-based persistence** to save all data across server restarts:

- **Data File**: `backend/data/store.json` (automatically created)
- **What's Persisted**:
  - All shopping carts
  - All orders (with full order history)
  - All discount codes (including usage status)
  - Order count (for nth-order discount generation)
- **Automatic Save**: Data is automatically saved after every operation (add item, checkout, generate discount code, etc.)
- **Automatic Load**: Data is automatically loaded when the server starts

**Note**: The `data/` directory is gitignored, so each environment maintains its own data file.

## Assumptions

1. **File-Based Persistence**: Data is stored in a JSON file (`data/store.json`) and persists across server restarts
2. **User ID**: The application uses a simple user_id string (no authentication system)
3. **N Value**: Default is 5 (every 5th order generates a discount code). This can be configured in the Store class
4. **Discount Percentage**: Fixed at 10% for all discount codes

## Testing

The project includes comprehensive unit tests covering:
- Store functionality (cart operations, order creation, discount codes)
- API endpoints (cart, checkout, admin)

Run tests with:
```bash
cd backend
pytest
```

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **Pytest**: Testing framework

### Frontend
- **React**: UI library
- **TypeScript**: Type-safe JavaScript
- **Axios**: HTTP client for API calls

## License

This project is created for demonstration purposes.


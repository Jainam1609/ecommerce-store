# Backend Implementation Details

This document provides a comprehensive explanation of the backend implementation, including detailed flow diagrams, logical reasoning, and sample dry runs for all possible scenarios.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Data Persistence](#data-persistence)
3. [Data Models](#data-models)
4. [Core Components](#core-components)
5. [API Flow Diagrams](#api-flow-diagrams)
6. [Detailed Flow Explanations](#detailed-flow-explanations)
7. [Sample Dry Runs](#sample-dry-runs)
8. [Edge Cases and Error Handling](#edge-cases-and-error-handling)

## Architecture Overview

The backend is built using **FastAPI**, a modern Python web framework. The architecture follows a clean separation of concerns:

### API Documentation (Swagger UI)

FastAPI automatically generates interactive API documentation using Swagger UI. The Swagger implementation includes:

- **Enhanced Metadata**: Detailed descriptions, tags, and contact information
- **Tag Organization**: Endpoints grouped by functionality (cart, checkout, admin)
- **Request/Response Schemas**: Automatic schema generation from Pydantic models
- **Interactive Testing**: Test endpoints directly from the browser
- **OpenAPI 3.0 Compliance**: Standard API specification

**Access Points:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

The Swagger documentation is automatically generated from:
- Function docstrings
- Pydantic model definitions
- Route decorators and parameters
- Response models

This ensures the documentation is always in sync with the code.

## Data Persistence

The application implements **JSON file-based persistence** to ensure data survives server restarts.

### Persistence Mechanism

**Storage Location:**
- Default: `backend/data/store.json`
- Automatically created if it doesn't exist
- Directory is created automatically if needed

**What Gets Persisted:**
- All shopping carts (by user_id)
- All orders (complete order history)
- All discount codes (including usage status and timestamps)
- Order count (for nth-order discount generation)
- Configuration (n value)

**Persistence Flow:**

1. **On Server Start:**
   ```
   Store.__init__() → _load_data()
   → Reads data/store.json if exists
   → Restores carts, orders, discount codes, order_count
   → If file doesn't exist, starts with empty store
   ```

2. **On Write Operations:**
   ```
   Any write operation (add_item, checkout, etc.)
   → Performs the operation
   → Calls _save_data()
   → Writes to data/store.json atomically
   ```

**Atomic Writes:**
- Data is written to a temporary file first (`store.json.tmp`)
- Then atomically renamed to `store.json`
- Prevents data corruption if server crashes during write

**Error Handling:**
- If file is corrupted or missing, store starts fresh (logs warning)
- If save fails, operation continues (logs error but doesn't crash)
- Graceful degradation ensures API remains functional

**Data Format:**
```json
{
  "n": 5,
  "order_count": 10,
  "carts": {
    "user1": {
      "user_id": "user1",
      "items": [...]
    }
  },
  "orders": [...],
  "discount_codes": [...]
}
```

**Benefits:**
- Data persists across server restarts
- No external database required
- Easy backup (just copy JSON file)
- Human-readable format for debugging
- Simple to reset (delete JSON file)

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│  (main.py - Entry Point)                │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼────────┐
│   Routers   │  │  Store (State)│
│             │  │                │
│ - cart.py   │  │ - Carts        │
│ - checkout  │  │ - Orders       │
│ - admin.py  │  │ - Discounts    │
└──────┬──────┘  └────────────────┘
       │
┌──────▼──────────┐
│  Data Models    │
│  (models.py)    │
└─────────────────┘
```

### Key Design Decisions

1. **File-Based Persistence**: All data is stored in memory during runtime but automatically persisted to a JSON file (`data/store.json`). This provides:
   - Data persistence across server restarts
   - No external database required
   - Simple backup/restore (just copy the JSON file)
   - Easy debugging (human-readable JSON format)

2. **Single Store Instance**: The `Store` class is instantiated once in `main.py` and shared across all API endpoints via `app.state.store`. This ensures data consistency.

3. **Automatic Persistence**: Data is automatically saved after every write operation:
   - Adding items to cart
   - Removing items from cart
   - Creating orders
   - Generating discount codes
   - Clearing carts

4. **Atomic Writes**: Data is saved using atomic file operations (write to temp file, then rename) to prevent corruption during server crashes.

5. **Pydantic Models**: All data structures use Pydantic models for automatic validation and serialization.

6. **RESTful API Design**: Endpoints follow REST conventions for clarity and maintainability.

## Data Models

### CartItem
```python
{
    "item_id": str,      # Unique identifier for the item
    "name": str,         # Display name
    "price": float,      # Price per unit (must be > 0)
    "quantity": int      # Quantity in cart (must be > 0)
}
```

### Cart
```python
{
    "user_id": str,      # Owner of the cart
    "items": [CartItem]  # List of items
}
```

### Order
```python
{
    "order_id": str,           # Format: "ORD-000001"
    "user_id": str,
    "items": [dict],           # Snapshot of cart items
    "subtotal": float,         # Sum of all items
    "discount_code": str|null,  # Applied discount code
    "discount_amount": float,  # Discount value (10% of subtotal)
    "total": float,            # Final amount after discount
    "created_at": datetime     # Order timestamp
}
```

### DiscountCode
```python
{
    "code": str,              # Format: "SAVE10-0001"
    "discount_percent": 10,   # Always 10%
    "created_at": datetime,   # Generation timestamp
    "used": bool,             # Whether code has been used
    "used_at": datetime|null  # When it was used
}
```

## Core Components

### Store Class

The `Store` class is the heart of the application. It maintains all state in memory during runtime and automatically persists it to a JSON file for durability across server restarts.

**State Variables:**
- `carts: Dict[str, Cart]` - Maps user_id to their cart
- `orders: List[Order]` - All orders ever placed
- `discount_codes: List[DiscountCode]` - All generated discount codes
- `n: int` - Every nth order generates a discount (default: 5)
- `order_count: int` - Total number of orders placed
- `data_file: str` - Path to JSON file for persistence (default: "data/store.json")

**Key Methods:**

1. **`get_or_create_cart(user_id)`**: Returns existing cart or creates a new empty one
2. **`add_item_to_cart(...)`**: Adds item to cart, or increments quantity if item exists (auto-saves)
3. **`remove_item_from_cart(user_id, item_id)`**: Removes specific item from cart (auto-saves)
4. **`get_cart(user_id)`**: Retrieves user's cart
5. **`clear_cart(user_id)`**: Deletes user's cart (auto-saves)
6. **`create_order(user_id, discount_code)`**: Creates order from cart, validates discount, generates new discount if nth order (auto-saves)
7. **`validate_discount_code(code)`**: Checks if code exists and is unused
8. **`generate_discount_code()`**: Creates a new discount code (auto-saves)
9. **`get_statistics()`**: Calculates and returns store statistics
10. **`_load_data()`**: Private method that loads data from JSON file on initialization
11. **`_save_data()`**: Private method that saves current state to JSON file (called after write operations)

## API Flow Diagrams

### Add Item to Cart Flow

```
Client Request
    │
    ▼
POST /api/cart/{user_id}/add
    │
    ▼
Cart Router (cart.py)
    │
    ▼
Validate Request Body (Pydantic)
    │
    ▼
Store.add_item_to_cart()
    │
    ├─► Get or create cart for user
    │
    ├─► Check if item already exists
    │   ├─► YES: Increment quantity → Save data
    │   └─► NO: Add new item → Save data
    │
    ▼
Return Updated Cart
```

### Checkout Flow

```
Client Request
    │
    ▼
POST /api/checkout/{user_id}
    │
    ▼
Checkout Router (checkout.py)
    │
    ▼
Store.create_order()
    │
    ├─► Validate cart exists and not empty
    │   └─► ERROR: "Cart is empty"
    │
    ├─► Calculate subtotal
    │
    ├─► If discount_code provided:
    │   ├─► Validate discount code
    │   │   ├─► Code exists? ──NO──► ERROR: "Invalid code"
    │   │   └─► Code unused? ──NO──► ERROR: "Already used"
    │   │
    │   ├─► Calculate discount (10% of subtotal)
    │   └─► Mark code as used
    │
    ├─► Calculate total (subtotal - discount)
    │
    ├─► Create Order object
    │
    ├─► Add order to orders list
    │
    ├─► Increment order_count
    │
    ├─► Check if order_count % n == 0
    │   └─► YES: Generate new discount code
    │
    ├─► Clear user's cart
    │
    ├─► Save data to JSON file (persist order and discount code)
    │
    ▼
Return Order Details
```

### Discount Code Generation Flow

```
Order Placed (create_order)
    │
    ▼
order_count += 1
    │
    ▼
Is order_count % n == 0?
    │
    ├─► NO: Continue
    │
    └─► YES: generate_discount_code()
        │
        ├─► Create code: "SAVE10-XXXX"
        │   (XXXX = sequential number)
        │
        ├─► Create DiscountCode object
        │   - used = False
        │   - created_at = now()
        │
        └─► Add to discount_codes list
```

## Detailed Flow Explanations

### 1. Adding Items to Cart

**Logical Reasoning:**
- When a user adds an item, we first check if they have a cart. If not, we create one.
- We then check if the item already exists in the cart (by `item_id`).
- If it exists, we increment the quantity (prevents duplicate entries).
- If it doesn't exist, we add it as a new cart item.
- This approach ensures data consistency and prevents cart bloat.

**Why increment quantity instead of creating duplicates?**
- Better user experience: Users expect quantity to increase when adding the same item
- Cleaner data: One entry per unique item
- Easier calculations: No need to sum quantities later

### 2. Checkout Process

**Logical Reasoning:**
The checkout process is the most complex operation. Here's the step-by-step reasoning:

1. **Cart Validation**: First, we ensure the cart exists and has items. This prevents creating empty orders.

2. **Subtotal Calculation**: We calculate the sum of (price × quantity) for all items. This is done before discount to ensure accurate calculations.

3. **Discount Validation**: If a discount code is provided:
   - We search through all discount codes
   - Check if the code matches AND is unused
   - If invalid, we raise an error immediately (fail-fast principle)
   - If valid, we calculate 10% of subtotal and mark the code as used

4. **Order Creation**: We create an order with:
   - Unique order ID (format: ORD-000001)
   - Snapshot of cart items (using `model_dump()` to convert to dict)
   - All financial calculations
   - Timestamp

5. **Discount Code Generation**: After order creation:
   - We increment `order_count`
   - Check if `order_count % n == 0` (every nth order)
   - If true, generate a new discount code
   - This happens AFTER order creation to ensure the order is counted

6. **Cart Clearing**: Finally, we clear the cart since items are now in an order.

**Why generate discount AFTER order creation?**
- Ensures the order is fully processed before generating the reward
- Maintains consistency: order_count reflects actual orders
- Prevents race conditions: discount generation is atomic with order creation

### 3. Discount Code System

**Logical Reasoning:**

The discount code system follows these rules:
1. **Generation**: Codes are generated every nth order (default: 5)
2. **Single Use**: Each code can only be used once
3. **Sequential**: Codes are numbered sequentially (SAVE10-0001, SAVE10-0002, etc.)
4. **10% Discount**: All codes provide 10% off the entire order

**Why every nth order?**
- Encourages repeat purchases
- Fair distribution: Not every order gets a discount
- Creates scarcity: Makes discount codes valuable

**Why single-use?**
- Prevents abuse: Users can't reuse the same code
- Ensures fairness: Each code benefits one customer
- Matches real-world behavior: Most discount codes are single-use

**Implementation Details:**
- Codes are stored in a list, not a dictionary, to preserve order
- When validating, we search linearly (acceptable for small scale)
- When used, we mark `used=True` and set `used_at=datetime.now()`
- This allows tracking of code usage history

### 4. Statistics Calculation

**Logical Reasoning:**

Statistics are calculated on-demand (not cached) to ensure accuracy:

1. **Total Items Purchased**: Sum of all quantities across all orders
2. **Total Purchase Amount**: Sum of all order totals (after discounts)
3. **Total Discount Amount**: Sum of all discount amounts applied
4. **Discount Codes List**: All codes with their status
5. **Total Orders**: Length of orders list

**Why calculate on-demand?**
- Always accurate: No risk of stale data
- Simple implementation: No need to maintain counters
- Acceptable performance: For file-based store, calculation is fast

## Sample Dry Runs

### Dry Run 1: Basic Cart Operations

**Scenario**: User adds items to cart and views cart

**Step 1: Add First Item**
```
Request: POST /api/cart/user1/add
Body: {
    "item_id": "item1",
    "name": "Laptop",
    "price": 999.99,
    "quantity": 1
}

Store State Before:
- carts: {}
- orders: []
- discount_codes: []
- order_count: 0

Execution:
1. get_or_create_cart("user1")
   → Creates new cart: Cart(user_id="user1", items=[])
2. Check if "item1" exists in cart → NO
3. Add CartItem(item_id="item1", name="Laptop", price=999.99, quantity=1)

Store State After:
- carts: {
    "user1": Cart(
        user_id="user1",
        items=[CartItem(item_id="item1", name="Laptop", price=999.99, quantity=1)]
    )
  }
- orders: []
- discount_codes: []
- order_count: 0
- Data saved to JSON file

Response: {
    "user_id": "user1",
    "items": [
        {
            "item_id": "item1",
            "name": "Laptop",
            "price": 999.99,
            "quantity": 1
        }
    ]
}
```

**Step 2: Add Same Item Again (Increment Quantity)**
```
Request: POST /api/cart/user1/add
Body: {
    "item_id": "item1",
    "name": "Laptop",
    "price": 999.99,
    "quantity": 2
}

Store State Before:
- carts: {"user1": Cart with 1 item (quantity=1)}

Execution:
1. get_or_create_cart("user1") → Returns existing cart
2. Check if "item1" exists → YES
3. Increment quantity: 1 + 2 = 3

Store State After:
- carts: {
    "user1": Cart(
        user_id="user1",
        items=[CartItem(item_id="item1", name="Laptop", price=999.99, quantity=3)]
    )
  }
- Data saved to JSON file

Response: {
    "user_id": "user1",
    "items": [
        {
            "item_id": "item1",
            "name": "Laptop",
            "price": 999.99,
            "quantity": 3
        }
    ]
}
```

**Step 3: Add Different Item**
```
Request: POST /api/cart/user1/add
Body: {
    "item_id": "item2",
    "name": "Mouse",
    "price": 29.99,
    "quantity": 1
}

Store State Before:
- carts: {"user1": Cart with 1 item (Laptop, qty=3)}

Execution:
1. get_or_create_cart("user1") → Returns existing cart
2. Check if "item2" exists → NO
3. Add new CartItem(item_id="item2", name="Mouse", price=29.99, quantity=1)

Store State After:
- carts: {
    "user1": Cart(
        user_id="user1",
        items=[
            CartItem(item_id="item1", name="Laptop", price=999.99, quantity=3),
            CartItem(item_id="item2", name="Mouse", price=29.99, quantity=1)
        ]
    )
  }
- Data saved to JSON file

Response: {
    "user_id": "user1",
    "items": [
        {"item_id": "item1", "name": "Laptop", "price": 999.99, "quantity": 3},
        {"item_id": "item2", "name": "Mouse", "price": 29.99, "quantity": 1}
    ]
}
```

### Dry Run 2: Checkout Without Discount

**Scenario**: User checks out with no discount code

**Initial State:**
```
- carts: {
    "user1": Cart(
        items=[
            CartItem(item_id="item1", name="Laptop", price=999.99, quantity=1),
            CartItem(item_id="item2", name="Mouse", price=29.99, quantity=2)
        ]
    )
  }
- orders: []
- discount_codes: []
- order_count: 0
- n = 5
```

**Request:**
```
POST /api/checkout/user1
Body: {}
```

**Execution:**
```
1. get_cart("user1")
   → Returns cart with 2 items

2. Validate cart exists and not empty
   → Cart exists, has items ✓

3. Calculate subtotal:
   - item1: 999.99 × 1 = 999.99
   - item2: 29.99 × 2 = 59.98
   - subtotal = 999.99 + 59.98 = 1059.97

4. discount_code provided? → NO
   - discount_amount = 0.0
   - applied_discount_code = None

5. Calculate total:
   - total = 1059.97 - 0.0 = 1059.97

6. Create Order:
   Order(
       order_id="ORD-000001",
       user_id="user1",
       items=[
           {"item_id": "item1", "name": "Laptop", "price": 999.99, "quantity": 1},
           {"item_id": "item2", "name": "Mouse", "price": 29.99, "quantity": 2}
       ],
       subtotal=1059.97,
       discount_code=None,
       discount_amount=0.0,
       total=1059.97,
       created_at=datetime.now()
   )

7. Append order to orders list

8. Increment order_count: 0 → 1

9. Check if order_count % n == 0:
   - 1 % 5 == 0? → NO
   - Skip discount code generation

10. clear_cart("user1")
    - Delete carts["user1"]
    - Save data

11. Save data to JSON file (persist order)

```

**Final State:**
```
- carts: {}  (cart cleared)
- orders: [
    Order(order_id="ORD-000001", user_id="user1", total=1059.97, ...)
  ]
- discount_codes: []  (no code generated, not 5th order)
- order_count: 1
- Data persisted to JSON file
```

**Response:**
```json
{
    "order_id": "ORD-000001",
    "user_id": "user1",
    "items": [
        {"item_id": "item1", "name": "Laptop", "price": 999.99, "quantity": 1},
        {"item_id": "item2", "name": "Mouse", "price": 29.99, "quantity": 2}
    ],
    "subtotal": 1059.97,
    "discount_code": null,
    "discount_amount": 0.0,
    "total": 1059.97,
    "created_at": "2024-01-15T10:30:00"
}
```

### Dry Run 3: Checkout with Valid Discount Code

**Scenario**: User checks out with a valid, unused discount code

**Initial State:**
```
- carts: {
    "user1": Cart(
        items=[CartItem(item_id="item1", name="Laptop", price=1000.00, quantity=1)]
    )
  }
- orders: []
- discount_codes: [
    DiscountCode(
        code="SAVE10-0001",
        discount_percent=10,
        created_at=datetime(2024-01-15, 10:00:00),
        used=False,
        used_at=None
    )
  ]
- order_count: 0
```

**Request:**
```
POST /api/checkout/user1
Body: {
    "discount_code": "SAVE10-0001"
}
```

**Execution:**
```
1. get_cart("user1") → Returns cart

2. Validate cart → ✓

3. Calculate subtotal:
   - subtotal = 1000.00 × 1 = 1000.00

4. discount_code provided? → YES ("SAVE10-0001")

5. validate_discount_code("SAVE10-0001"):
   - Loop through discount_codes
   - Find: DiscountCode(code="SAVE10-0001", used=False)
   - Code exists? → YES
   - Code unused? → YES
   - Return discount object ✓

6. Calculate discount:
   - discount_amount = 1000.00 × 0.10 = 100.00
   - applied_discount_code = "SAVE10-0001"

7. Mark discount as used:
   - discount.used = True
   - discount.used_at = datetime.now()

8. Calculate total:
   - total = 1000.00 - 100.00 = 900.00

9. Create Order:
   Order(
       order_id="ORD-000001",
       user_id="user1",
       items=[...],
       subtotal=1000.00,
       discount_code="SAVE10-0001",
       discount_amount=100.00,
       total=900.00,
       created_at=datetime.now()
   )

10. Append order, increment order_count: 0 → 1

11. Check if 1 % 5 == 0? → NO (skip generation)

12. Clear cart

13. Save data to JSON file (persist order and discount code changes)

```

**Final State:**
```
- carts: {}
- orders: [Order(order_id="ORD-000001", discount_code="SAVE10-0001", total=900.00)]
- discount_codes: [
    DiscountCode(
        code="SAVE10-0001",
        used=True,  ← Changed
        used_at=datetime(2024-01-15, 10:30:00)  ← Set
    )
  ]
- order_count: 1
- Data persisted to JSON file
```

**Response:**
```json
{
    "order_id": "ORD-000001",
    "user_id": "user1",
    "items": [...],
    "subtotal": 1000.00,
    "discount_code": "SAVE10-0001",
    "discount_amount": 100.00,
    "total": 900.00,
    "created_at": "2024-01-15T10:30:00"
}
```

### Dry Run 4: Checkout with Invalid Discount Code

**Scenario**: User tries to use a discount code that doesn't exist

**Initial State:**
```
- carts: {"user1": Cart with items}
- discount_codes: []  (no codes exist)
```

**Request:**
```
POST /api/checkout/user1
Body: {
    "discount_code": "INVALID-CODE"
}
```

**Execution:**
```
1. get_cart("user1") → Returns cart
2. Validate cart → ✓
3. Calculate subtotal → 1000.00
4. discount_code provided? → YES ("INVALID-CODE")
5. validate_discount_code("INVALID-CODE"):
   - Loop through discount_codes
   - No matching code found
   - Return None
6. Since discount is None:
   - Raise ValueError("Invalid or already used discount code")
```

**Result:**
- HTTP 400 Bad Request
- Response: `{"detail": "Invalid or already used discount code"}`
- Cart remains unchanged
- No order created

### Dry Run 5: Checkout with Already-Used Discount Code

**Scenario**: User tries to reuse a discount code

**Initial State:**
```
- carts: {"user1": Cart with items}
- discount_codes: [
    DiscountCode(
        code="SAVE10-0001",
        used=True,  ← Already used
        used_at=datetime(2024-01-15, 10:00:00)
    )
  ]
```

**Request:**
```
POST /api/checkout/user1
Body: {
    "discount_code": "SAVE10-0001"
}
```

**Execution:**
```
1-3. Same as before (get cart, validate, calculate subtotal)
4. validate_discount_code("SAVE10-0001"):
   - Find: DiscountCode(code="SAVE10-0001", used=True)
   - Code exists? → YES
   - Code unused? → NO (used=True)
   - Return None
5. Raise ValueError("Invalid or already used discount code")
```

**Result:**
- HTTP 400 Bad Request
- Response: `{"detail": "Invalid or already used discount code"}`
- Cart remains unchanged

### Dry Run 6: Automatic Discount Code Generation (5th Order)

**Scenario**: User places 5 orders, triggering automatic discount code generation

**Initial State:**
```
- carts: {"user1": Cart with items}
- orders: []  (0 orders so far)
- discount_codes: []
- order_count: 0
- n = 5
```

**Execution Sequence:**

**Order 1:**
```
- Checkout without discount
- order_count: 0 → 1
- 1 % 5 == 0? → NO
- No discount code generated
```

**Order 2:**
```
- order_count: 1 → 2
- 2 % 5 == 0? → NO
- No discount code generated
```

**Order 3:**
```
- order_count: 2 → 3
- 3 % 5 == 0? → NO
- No discount code generated
```

**Order 4:**
```
- order_count: 3 → 4
- 4 % 5 == 0? → NO
- No discount code generated
```

**Order 5 (The Critical One):**
```
Request: POST /api/checkout/user1
Body: {}

Execution:
1-6. Normal checkout process (no discount)
7. Create order: Order(order_id="ORD-000005", ...)
8. Append order
9. Increment order_count: 4 → 5
10. Check if 5 % 5 == 0? → YES!
11. generate_discount_code():
    - code = "SAVE10-0001"  (len(discount_codes) + 1 = 0 + 1 = 1)
    - Create DiscountCode(
          code="SAVE10-0001",
          discount_percent=10,
          created_at=datetime.now(),
          used=False,
          used_at=None
      )
    - Append to discount_codes list
    - Save data

12. Clear cart
    - Save data

13. Save data to JSON file (persist order and new discount code)

```

**Final State After Order 5:**
```
- orders: [Order1, Order2, Order3, Order4, Order5]
- discount_codes: [
    DiscountCode(
        code="SAVE10-0001",
        used=False,  ← Available for next order!
        created_at=datetime.now()
    )
  ]
- order_count: 5
- Data persisted to JSON file
```

**Next Order (Order 6):**
```
- User can now use "SAVE10-0001" in checkout
- After Order 6: order_count = 6, 6 % 5 != 0, no new code
- After Order 7: order_count = 7, 7 % 5 != 0, no new code
- After Order 8: order_count = 8, 8 % 5 != 0, no new code
- After Order 9: order_count = 9, 9 % 5 != 0, no new code
- After Order 10: order_count = 10, 10 % 5 == 0, generate "SAVE10-0002"
```

### Dry Run 7: Statistics Calculation

**Scenario**: Admin requests statistics after multiple orders

**Initial State:**
```
- orders: [
    Order1: items=[item1(qty=2), item2(qty=1)], total=150.00, discount_amount=0.00,
    Order2: items=[item3(qty=3)], total=300.00, discount_amount=30.00,
    Order3: items=[item1(qty=1)], total=50.00, discount_amount=0.00
  ]
- discount_codes: [
    DiscountCode(code="SAVE10-0001", used=True),
    DiscountCode(code="SAVE10-0002", used=False)
  ]
```

**Request:**
```
GET /api/admin/statistics
```

**Execution:**
```
1. Calculate total_items_purchased:
   - Order1: 2 + 1 = 3 items
   - Order2: 3 items
   - Order3: 1 item
   - Total = 3 + 3 + 1 = 7 items

2. Calculate total_purchase_amount:
   - Sum of all order totals: 150.00 + 300.00 + 50.00 = 500.00

3. Calculate total_discount_amount:
   - Sum of discount_amount: 0.00 + 30.00 + 0.00 = 30.00

4. Build discount_codes_list:
   - [
       {
         "code": "SAVE10-0001",
         "created_at": "2024-01-15T10:00:00",
         "used": True,
         "used_at": "2024-01-15T10:30:00"
       },
       {
         "code": "SAVE10-0002",
         "created_at": "2024-01-15T11:00:00",
         "used": False,
         "used_at": null
       }
     ]

5. total_orders = len(orders) = 3
```

**Response:**
```json
{
    "total_items_purchased": 7,
    "total_purchase_amount": 500.00,
    "total_discount_amount": 30.00,
    "discount_codes": [
        {
            "code": "SAVE10-0001",
            "created_at": "2024-01-15T10:00:00",
            "used": true,
            "used_at": "2024-01-15T10:30:00"
        },
        {
            "code": "SAVE10-0002",
            "created_at": "2024-01-15T11:00:00",
            "used": false,
            "used_at": null
        }
    ],
    "total_orders": 3
}
```

### Dry Run 8: Multiple Users with Separate Carts

**Scenario**: Two different users add items and checkout independently

**Initial State:**
```
- carts: {}
- orders: []
```

**Step 1: User1 adds items**
```
POST /api/cart/user1/add
Body: {"item_id": "item1", "name": "Laptop", "price": 1000.00, "quantity": 1}

State:
- carts: {
    "user1": Cart(items=[CartItem(item_id="item1", ...)])
  }
```

**Step 2: User2 adds items**
```
POST /api/cart/user2/add
Body: {"item_id": "item2", "name": "Phone", "price": 500.00, "quantity": 1}

State:
- carts: {
    "user1": Cart(items=[CartItem(item_id="item1", ...)]),
    "user2": Cart(items=[CartItem(item_id="item2", ...)])
  }
```

**Step 3: User1 checks out**
```
POST /api/checkout/user1

Execution:
- Only user1's cart is processed
- user1's cart is cleared
- user2's cart remains intact

State After:
- carts: {
    "user2": Cart(items=[CartItem(item_id="item2", ...)])  ← Still exists!
  }
- orders: [Order(user_id="user1", ...)]
```

**Step 4: User2 checks out**
```
POST /api/checkout/user2

State After:
- carts: {}  (both carts cleared)
- orders: [
    Order(user_id="user1", ...),
    Order(user_id="user2", ...)
  ]
```

**Key Point**: Each user has an independent cart. Operations on one user's cart don't affect others.

## Edge Cases and Error Handling

### Edge Case 1: Empty Cart Checkout

**Scenario**: User tries to checkout with empty cart

**Request:**
```
POST /api/checkout/user1
Body: {}
```

**State:**
```
- carts: {"user1": Cart(items=[])}  ← Empty cart
```

**Execution:**
```
1. get_cart("user1") → Returns cart
2. Check: cart.items is empty? → YES
3. Raise ValueError("Cart is empty")
```

**Result:**
- HTTP 400 Bad Request
- Response: `{"detail": "Cart is empty"}`
- Cart remains unchanged

### Edge Case 2: Checkout for Non-Existent User

**Scenario**: User tries to checkout without ever adding items

**Request:**
```
POST /api/checkout/user1
Body: {}
```

**State:**
```
- carts: {}  ← No cart for user1
```

**Execution:**
```
1. get_cart("user1") → Returns None
2. Check: cart is None or cart.items is empty? → YES (None)
3. Raise ValueError("Cart is empty")
```

**Result:**
- HTTP 400 Bad Request
- Same error as empty cart (intentional: both are "empty" scenarios)

### Edge Case 3: Adding Item with Zero or Negative Price

**Scenario**: Invalid price validation

**Request:**
```
POST /api/cart/user1/add
Body: {
    "item_id": "item1",
    "name": "Product",
    "price": -10.00,  ← Invalid
    "quantity": 1
}
```

**Execution:**
```
1. Pydantic validation in AddItemRequest model
2. Field(gt=0) validation fails
3. FastAPI automatically returns HTTP 422 Unprocessable Entity
```

**Result:**
- HTTP 422 Validation Error
- Response includes detailed validation errors

### Edge Case 4: Removing Non-Existent Item

**Scenario**: User tries to remove item that doesn't exist in cart

**Request:**
```
DELETE /api/cart/user1/item/nonexistent
```

**State:**
```
- carts: {
    "user1": Cart(items=[CartItem(item_id="item1", ...)])
  }
```

**Execution:**
```
1. remove_item_from_cart("user1", "nonexistent")
2. Filter items: Keep all items where item_id != "nonexistent"
3. Result: Cart with same items (item1 still there)
4. Return updated cart (no error, item just wasn't removed)
```

**Result:**
- HTTP 200 OK
- Cart returned unchanged (idempotent operation)

### Edge Case 5: Discount Code Applied to Zero Subtotal

**Scenario**: Edge case where subtotal calculation results in zero (shouldn't happen, but handled)

**Note**: This is prevented by validation (price > 0, quantity > 0), but if it occurred:

**Execution:**
```
- subtotal = 0.00
- discount_amount = 0.00 × 0.10 = 0.00
- total = 0.00 - 0.00 = 0.00
```

**Result:**
- Order created successfully with $0.00 total
- Discount code still marked as used (by design)

### Edge Case 6: Concurrent Requests (Race Condition)

**Scenario**: Two requests try to use the same discount code simultaneously

**Note**: In a production system with multiple workers, this could be an issue. However:
- Our file-based store with single instance handles this naturally
- FastAPI processes requests sequentially in development mode
- For production, would need database transactions or locks

**Current Behavior:**
- First request validates code → finds unused code → marks as used → proceeds
- Second request validates code → finds used code → returns error
- Works correctly due to sequential processing

## Summary

The implementation follows these key principles:

1. **Simplicity**: File-based persistence keeps the code simple and easy to understand
2. **Validation**: Input validation at multiple levels (Pydantic, business logic)
3. **Consistency**: Single source of truth (Store instance) ensures data consistency
4. **Error Handling**: Clear error messages for all failure scenarios
5. **Idempotency**: Operations like remove_item are safe to retry
6. **Atomicity**: Order creation and discount code generation happen atomically
7. **Fairness**: Discount codes are generated fairly (every nth order) and used once
8. **Persistence**: All data is automatically saved to JSON file after write operations

The system handles all required scenarios and edge cases while maintaining code clarity and maintainability.


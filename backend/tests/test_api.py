"""
Unit tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from app.store import Store

@pytest.fixture
def client():
    """Create a test client with isolated store"""
    import tempfile
    import os
    # Create a temporary data file for each test
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    
    # Create a new store instance for testing with isolated data file
    store = Store(n=5, data_file=temp_file.name)
    app.state.store = store
    
    yield TestClient(app)
    
    # Cleanup: remove temporary file after test
    try:
        os.unlink(temp_file.name)
    except:
        pass

class TestCartAPI:
    """Test cases for Cart API endpoints"""
    
    def test_add_item_to_cart(self, client):
        """Test adding item to cart via API"""
        response = client.post(
            "/api/cart/user1/add",
            json={"item_id": "item1", "name": "Product 1", "price": 10.0, "quantity": 2}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user1"
        assert len(data["items"]) == 1
        assert data["items"][0]["item_id"] == "item1"
    
    def test_get_cart(self, client):
        """Test getting cart via API"""
        # Add item first
        client.post(
            "/api/cart/user1/add",
            json={"item_id": "item1", "name": "Product 1", "price": 10.0, "quantity": 2}
        )
        
        response = client.get("/api/cart/user1")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user1"
        assert len(data["items"]) == 1
    
    def test_remove_item_from_cart(self, client):
        """Test removing item from cart via API"""
        # Add item first
        client.post(
            "/api/cart/user1/add",
            json={"item_id": "item1", "name": "Product 1", "price": 10.0, "quantity": 2}
        )
        
        response = client.delete("/api/cart/user1/item/item1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
    
    def test_clear_cart(self, client):
        """Test clearing cart via API"""
        # Add item first
        client.post(
            "/api/cart/user1/add",
            json={"item_id": "item1", "name": "Product 1", "price": 10.0, "quantity": 2}
        )
        
        response = client.delete("/api/cart/user1/clear")
        assert response.status_code == 200
        
        # Verify cart is empty
        response = client.get("/api/cart/user1")
        assert len(response.json()["items"]) == 0

class TestCheckoutAPI:
    """Test cases for Checkout API endpoints"""
    
    def test_checkout_without_discount(self, client):
        """Test checkout without discount code"""
        # Add items to cart
        client.post(
            "/api/cart/user1/add",
            json={"item_id": "item1", "name": "Product 1", "price": 10.0, "quantity": 2}
        )
        
        response = client.post(
            "/api/checkout/user1",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user1"
        assert data["subtotal"] == 20.0
        assert data["total"] == 20.0
        assert data["discount_code"] is None
    
    def test_checkout_with_valid_discount(self, client):
        """Test checkout with valid discount code"""
        # Generate discount code
        discount_response = client.post("/api/admin/discount-code/generate")
        discount_code = discount_response.json()["code"]
        
        # Add items to cart
        client.post(
            "/api/cart/user1/add",
            json={"item_id": "item1", "name": "Product 1", "price": 100.0, "quantity": 1}
        )
        
        response = client.post(
            "/api/checkout/user1",
            json={"discount_code": discount_code}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["discount_code"] == discount_code
        assert data["discount_amount"] == 10.0
        assert data["total"] == 90.0
    
    def test_checkout_with_invalid_discount(self, client):
        """Test checkout with invalid discount code"""
        # Add items to cart
        client.post(
            "/api/cart/user1/add",
            json={"item_id": "item1", "name": "Product 1", "price": 10.0, "quantity": 2}
        )
        
        response = client.post(
            "/api/checkout/user1",
            json={"discount_code": "INVALID"}
        )
        assert response.status_code == 400
    
    def test_checkout_empty_cart(self, client):
        """Test checkout with empty cart"""
        response = client.post(
            "/api/checkout/user1",
            json={}
        )
        assert response.status_code == 400

class TestAdminAPI:
    """Test cases for Admin API endpoints"""
    
    def test_generate_discount_code(self, client):
        """Test generating discount code via admin API"""
        response = client.post("/api/admin/discount-code/generate")
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert data["discount_percent"] == 10
        assert data["used"] is False
    
    def test_get_statistics(self, client):
        """Test getting statistics via admin API"""
        # Create some orders first
        client.post(
            "/api/cart/user1/add",
            json={"item_id": "item1", "name": "Product 1", "price": 10.0, "quantity": 2}
        )
        client.post("/api/checkout/user1", json={})
        
        response = client.get("/api/admin/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_items_purchased" in data
        assert "total_purchase_amount" in data
        assert "discount_codes" in data
        assert "total_discount_amount" in data
        assert data["total_orders"] == 1


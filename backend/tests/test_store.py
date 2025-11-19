"""
Unit tests for the Store class
"""
import pytest
import tempfile
import os
from app.store import Store
from app.models import CartItem

@pytest.fixture
def temp_store():
    """Create a store with temporary data file"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    store = Store(n=5, data_file=temp_file.name)
    yield store
    # Cleanup
    try:
        os.unlink(temp_file.name)
    except:
        pass

class TestStore:
    """Test cases for Store functionality"""
    
    def test_get_or_create_cart(self, temp_store):
        """Test creating a new cart"""
        cart = temp_store.get_or_create_cart("user1")
        assert cart.user_id == "user1"
        assert len(cart.items) == 0
    
    def test_add_item_to_cart(self, temp_store):
        """Test adding items to cart"""
        cart = temp_store.add_item_to_cart("user1", "item1", "Product 1", 10.0, 2)
        assert len(cart.items) == 1
        assert cart.items[0].item_id == "item1"
        assert cart.items[0].quantity == 2
    
    def test_add_same_item_twice(self, temp_store):
        """Test adding the same item twice increases quantity"""
        temp_store.add_item_to_cart("user1", "item1", "Product 1", 10.0, 2)
        cart = temp_store.add_item_to_cart("user1", "item1", "Product 1", 10.0, 3)
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 5
    
    def test_remove_item_from_cart(self, temp_store):
        """Test removing an item from cart"""
        temp_store.add_item_to_cart("user1", "item1", "Product 1", 10.0, 2)
        cart = temp_store.remove_item_from_cart("user1", "item1")
        assert len(cart.items) == 0
    
    def test_create_order(self, temp_store):
        """Test creating an order"""
        temp_store.add_item_to_cart("user1", "item1", "Product 1", 10.0, 2)
        order = temp_store.create_order("user1")
        assert order.user_id == "user1"
        assert order.subtotal == 20.0
        assert order.total == 20.0
        assert len(order.items) == 1
    
    def test_create_order_with_discount(self, temp_store):
        """Test creating an order with valid discount code"""
        # Generate a discount code
        discount = temp_store.generate_discount_code()
        temp_store.add_item_to_cart("user1", "item1", "Product 1", 100.0, 1)
        order = temp_store.create_order("user1", discount_code=discount.code)
        assert order.discount_code == discount.code
        assert order.discount_amount == 10.0  # 10% of 100
        assert order.total == 90.0
    
    def test_create_order_with_invalid_discount(self, temp_store):
        """Test creating an order with invalid discount code"""
        temp_store.add_item_to_cart("user1", "item1", "Product 1", 10.0, 2)
        with pytest.raises(ValueError, match="Invalid or already used discount code"):
            temp_store.create_order("user1", discount_code="INVALID")
    
    def test_discount_code_can_only_be_used_once(self, temp_store):
        """Test that discount code can only be used once"""
        discount = temp_store.generate_discount_code()
        temp_store.add_item_to_cart("user1", "item1", "Product 1", 10.0, 1)
        temp_store.create_order("user1", discount_code=discount.code)
        
        # Try to use the same code again
        temp_store.add_item_to_cart("user2", "item1", "Product 1", 10.0, 1)
        with pytest.raises(ValueError, match="Invalid or already used discount code"):
            temp_store.create_order("user2", discount_code=discount.code)
    
    def test_nth_order_generates_discount_code(self, temp_store):
        """Test that every nth order generates a discount code"""
        temp_store.n = 3  # Every 3rd order
        assert len(temp_store.discount_codes) == 0
        
        # Create 3 orders
        for i in range(3):
            temp_store.add_item_to_cart(f"user{i}", "item1", "Product 1", 10.0, 1)
            temp_store.create_order(f"user{i}")
        
        # Should have generated 1 discount code
        assert len(temp_store.discount_codes) == 1
    
    def test_get_statistics(self, temp_store):
        """Test getting store statistics"""
        temp_store.add_item_to_cart("user1", "item1", "Product 1", 10.0, 2)
        temp_store.add_item_to_cart("user1", "item2", "Product 2", 20.0, 1)
        temp_store.create_order("user1")
        
        stats = temp_store.get_statistics()
        assert stats["total_items_purchased"] == 3
        assert stats["total_purchase_amount"] == 40.0
        assert stats["total_orders"] == 1


"""
SmartCart - Automated Test Suite
Verifies authentication, catalog search, recommendations, cart operations,
checkout, admin telemetry, and machine learning components.
"""

import unittest
import json
from app import create_app
from database import db
from models import User, Customer, Product, Order, Cart, CartItem
from services.recommendation_service import recommendation_service
from services.similarity_service import similarity_engine
from services.association_service import association_engine

class SmartCartTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_homepage_loads(self):
        """Test homepage renders with HTTP 200."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SmartCart", response.data)
        self.assertIn(b"Recommended For You", response.data)

    def test_02_authentication_flow(self):
        """Test login with demo customer credentials and invalid credentials."""
        # Valid customer login
        res = self.client.post("/login", data={
            "email": "customer@smartcart.com",
            "password": "Customer@123"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Aarav Sharma", res.data)

        # Logout
        res = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Invalid login
        res = self.client.post("/login", data={
            "email": "customer@smartcart.com",
            "password": "WrongPassword!"
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", res.data)

    def test_03_admin_access_control(self):
        """Test that unauthenticated or customer users cannot access admin dashboard."""
        res = self.client.get("/admin/dashboard", follow_redirects=True)
        self.assertIn(b"Please log in as an administrator", res.data)

        # Log in as admin
        res = self.client.post("/login", data={
            "email": "admin@smartcart.com",
            "password": "Admin@123"
        }, follow_redirects=True)
        self.assertIn(b"Management & Analytics Hub", res.data)

        # Access admin dashboard
        res = self.client.get("/admin/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Total Customers", res.data)

    def test_04_product_search_and_filter(self):
        """Test product search query and category filters."""
        # Search by keyword
        res = self.client.get("/search?q=Headphones")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Products Found", res.data)

        # Category filter
        res = self.client.get("/search?category=Electronics")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Electronics", res.data)

    def test_05_product_details_and_recommendations(self):
        """Test product page details, similar items, and FBT bundle."""
        prod = Product.query.first()
        self.assertIsNotNone(prod)

        res = self.client.get(f"/product/{prod.product_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(prod.name.encode("utf-8"), res.data)
        self.assertIn(b"Similar Products", res.data)

    def test_06_recommendation_services_direct(self):
        """Test similarity engine, association engine, and ML recommendation service directly."""
        prod = Product.query.first()
        
        # Similar items
        similar = similarity_engine.get_similar_products(prod.product_id, top_n=4)
        self.assertTrue(len(similar) > 0)

        # Frequently bought together bundle
        fbt = association_engine.get_frequently_bought_together(prod.product_id, top_n=3)
        self.assertIsNotNone(fbt)
        self.assertEqual(fbt["primary_product"]["Product_ID"], prod.product_id)

        # Personalized recommendations
        cust = Customer.query.first()
        recs = recommendation_service.get_personalized_recommendations(
            customer_data=cust.to_dict(),
            top_n=6
        )
        self.assertTrue(len(recs) > 0)
        self.assertIn("match_percentage", recs[0])
        self.assertIn("recommendation_reason", recs[0])

    def test_07_cart_and_checkout_flow(self):
        """Test adding item to cart, updating quantity, and placing a demo order."""
        prod = Product.query.first()
        
        # Add to cart via AJAX API
        res = self.client.post("/api/cart/add", json={
            "product_id": prod.product_id,
            "quantity": 2
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["total_items"], 2)

        # View cart
        res = self.client.get("/cart")
        self.assertEqual(res.status_code, 200)
        self.assertIn(prod.name.encode("utf-8"), res.data)

        # Checkout page
        res = self.client.get("/checkout")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Delivery Address", res.data)

        # Place order
        res = self.client.post("/checkout", data={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+91 9876543210",
            "address": "123 Test Street",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560001",
            "payment_method": "UPI"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Order Confirmed!", res.data)

    def test_08_admin_analytics_api(self):
        """Test admin charts data API returns all 12 datasets."""
        # Log in as admin
        self.client.post("/login", data={
            "email": "admin@smartcart.com",
            "password": "Admin@123"
        })

        res = self.client.get("/admin/api/analytics/charts")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        
        # Verify keys for all 12 charts
        self.assertIn("daily_sales", data)
        self.assertIn("monthly_revenue", data)
        self.assertIn("orders_over_time", data)
        self.assertIn("sales_by_category", data)
        self.assertIn("top_products", data)
        self.assertIn("customer_growth", data)
        self.assertIn("funnel", data)
        self.assertIn("cart_rate", data)
        self.assertIn("conversion_rate", data)
        self.assertIn("rec_ctr", data)
        self.assertIn("rec_cvr", data)
        self.assertIn("daily_aov", data)

    def test_09_recommendation_tracking(self):
        """Test telemetry tracking when recommendation clicked."""
        prod = Product.query.first()
        res = self.client.post("/api/recommendations/track", json={
            "product_id": prod.product_id,
            "event_type": "click",
            "recommendation_type": "Personalized"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])

    def test_10_admin_product_management(self):
        """Test admin product CRUD operations."""
        self.client.post("/login", data={
            "email": "admin@smartcart.com",
            "password": "Admin@123"
        })
        
        # Add new product
        res = self.client.post("/admin/products", data={
            "action": "add",
            "name": "Unit Test Smart Device",
            "brand": "SmartCart Labs",
            "category": "Electronics",
            "subcategory": "Audio",
            "price": "2999.00",
            "discount": "15",
            "stock": "45",
            "description": "High performance smart gadget for unit test verification."
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Unit Test Smart Device", res.data)

    def test_11_admin_order_status_update(self):
        """Test admin updating order lifecycle status."""
        self.client.post("/login", data={
            "email": "admin@smartcart.com",
            "password": "Admin@123"
        })
        order = Order.query.first()
        self.assertIsNotNone(order)
        
        res = self.client.post("/admin/orders", data={
            "order_id": order.order_id,
            "status": "Delivered"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        
        updated = Order.query.filter_by(order_id=order.order_id).first()
        self.assertEqual(updated.status, "Delivered")

    def test_12_admin_dataset_export(self):
        """Test downloading dataset export CSV."""
        self.client.post("/login", data={
            "email": "admin@smartcart.com",
            "password": "Admin@123"
        })
        res = self.client.get("/admin/dataset/export")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("Content-Type"), "text/csv; charset=utf-8")
        self.assertTrue(len(res.data) > 0)

if __name__ == "__main__":
    unittest.main()

"""
SmartCart - Order and Checkout Processing Service
"""

import uuid
from datetime import datetime
from database import db
from models import Order, OrderItem, Product, Customer, Cart, CartItem

class OrderService:

    @staticmethod
    def get_or_create_cart(customer_id=None, session_id=None):
        """Retrieves or creates a shopping cart for a logged-in user or session."""
        cart = None
        if customer_id:
            cart = Cart.query.filter_by(customer_id=customer_id).first()
        elif session_id:
            cart = Cart.query.filter_by(session_id=session_id).first()
            
        if not cart:
            cart = Cart(customer_id=customer_id, session_id=session_id)
            db.session.add(cart)
            db.session.commit()
        return cart

    @staticmethod
    def get_cart_details(cart):
        """Computes subtotal, discount savings, delivery fee, and final total."""
        items_data = []
        subtotal = 0.0
        total_discount = 0.0
        
        for item in cart.items:
            product = Product.query.filter_by(product_id=item.product_id).first()
            if product:
                item_subtotal = round(product.price * item.quantity, 2)
                item_final = round(product.final_price * item.quantity, 2)
                item_savings = round(item_subtotal - item_final, 2)
                
                subtotal += item_subtotal
                total_discount += item_savings
                
                items_data.append({
                    "cart_item_id": item.id,
                    "product_id": product.product_id,
                    "name": product.name,
                    "brand": product.brand,
                    "category": product.category,
                    "image_url": product.image_url,
                    "price": product.price,
                    "discount": product.discount,
                    "final_price": product.final_price,
                    "quantity": item.quantity,
                    "item_subtotal": item_subtotal,
                    "item_final": item_final,
                    "stock": product.stock
                })
                
        final_product_total = round(subtotal - total_discount, 2)
        delivery_fee = 0.0 if (final_product_total >= 1000.0 or final_product_total == 0) else 99.0
        grand_total = round(final_product_total + delivery_fee, 2)
        
        return {
            "items": items_data,
            "items_count": sum(i["quantity"] for i in items_data),
            "subtotal": round(subtotal, 2),
            "total_discount": round(total_discount, 2),
            "delivery_fee": delivery_fee,
            "grand_total": grand_total
        }

    @staticmethod
    def place_order(customer_id, checkout_data, cart):
        """Creates an order, associates items, clears cart, and updates customer spend metrics."""
        cart_info = OrderService.get_cart_details(cart)
        if not cart_info["items"]:
            raise ValueError("Your cart is empty.")
            
        order_num = f"SC-2026-{uuid.uuid4().hex[:6].upper()}"
        
        order = Order(
            order_id=order_num,
            customer_id=customer_id,
            order_date=datetime.utcnow(),
            total_amount=cart_info["grand_total"],
            payment_method=checkout_data.get("payment_method", "UPI"),
            full_name=checkout_data.get("full_name", "Valued Customer"),
            email=checkout_data.get("email", "customer@example.com"),
            phone=checkout_data.get("phone", "9876543210"),
            address=checkout_data.get("address", "123 Street"),
            city=checkout_data.get("city", "Mumbai"),
            state=checkout_data.get("state", "Maharashtra"),
            pincode=checkout_data.get("pincode", "400001"),
            status="Placed"
        )
        db.session.add(order)
        db.session.flush()
        
        # Save order items & deduct stock
        for item_info in cart_info["items"]:
            oi = OrderItem(
                order_id=order_num,
                product_id=item_info["product_id"],
                quantity=item_info["quantity"],
                unit_price=item_info["price"],
                discount=item_info["discount"],
                total_price=item_info["item_final"]
            )
            db.session.add(oi)
            
            # Stock deduction
            prod = Product.query.filter_by(product_id=item_info["product_id"]).first()
            if prod:
                prod.stock = max(0, prod.stock - item_info["quantity"])
                
        # Clear cart
        for item in cart.items:
            db.session.delete(item)
            
        # Update customer stats
        cust = Customer.query.filter_by(customer_id=customer_id).first()
        if cust:
            cust.total_purchases = (cust.total_purchases or 0) + 1
            cust.average_order_value = round(((cust.average_order_value or 0.0) + order.total_amount) / 2, 2)
            cust.last_purchase_date = datetime.utcnow().strftime("%Y-%m-%d")
            
        db.session.commit()
        return order

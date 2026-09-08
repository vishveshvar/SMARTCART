"""
SmartCart - Order & Checkout Management Routes
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from database import db
from models import Order, OrderItem, Product, Customer, Cart, RecommendationLog
from services.order_service import OrderService
from routes.auth_routes import login_required

order_bp = Blueprint("order", __name__)

@order_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    customer_id = session.get("customer_id")
    session_id = session.get("cart_session_id")
    cart = OrderService.get_or_create_cart(customer_id=customer_id, session_id=session_id)
    cart_data = OrderService.get_cart_details(cart)
    
    if not cart_data["items"]:
        flash("Your cart is empty. Add some products before checking out.", "info")
        return redirect(url_for("product.search"))
        
    cust = Customer.query.filter_by(customer_id=customer_id).first() if customer_id else None
    
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip() or (cust.name if cust else "SmartCart Shopper")
        email = request.form.get("email", "").strip() or session.get("email", "customer@smartcart.com")
        phone = request.form.get("phone", "").strip() or "+91 9876543210"
        address = request.form.get("address", "").strip() or "42 MG Road"
        city = request.form.get("city", "").strip() or (cust.city if cust else "Mumbai")
        state = request.form.get("state", "").strip() or (cust.state if cust else "Maharashtra")
        pincode = request.form.get("pincode", "").strip() or "400001"
        payment_method = request.form.get("payment_method", "UPI")
        
        checkout_info = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "payment_method": payment_method
        }
        
        try:
            cid = customer_id or "GUEST_CUST"
            new_order = OrderService.place_order(cid, checkout_info, cart)
            
            # Update RecommendationLog if customer purchased a previously recommended item
            for item in cart_data["items"]:
                rec_log = RecommendationLog.query.filter_by(
                    customer_id=cid,
                    product_id=item["product_id"]
                ).first()
                if rec_log:
                    rec_log.purchased = 1
            db.session.commit()
            
            flash("Order placed successfully!", "success")
            return redirect(url_for("order.order_confirmation", order_id=new_order.order_id))
        except Exception as e:
            flash(f"Error creating order: {str(e)}", "danger")
            
    return render_template("checkout.html", cart=cart_data, customer=cust)

@order_bp.route("/order-confirmation/<order_id>")
def order_confirmation(order_id):
    order = Order.query.filter_by(order_id=order_id).first_or_404()
    
    # Calculate estimated delivery date (+4 days)
    order_dt = order.order_date or datetime.utcnow()
    expected_delivery = (order_dt + timedelta(days=4)).strftime("%A, %B %d, %Y")
    
    # Enrich item details
    items_with_details = []
    for item in order.items:
        prod = Product.query.filter_by(product_id=item.product_id).first()
        items_with_details.append({
            "product_id": item.product_id,
            "name": prod.name if prod else item.product_id,
            "brand": prod.brand if prod else "",
            "category": prod.category if prod else "",
            "image_url": prod.image_url if prod else "",
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "discount": item.discount,
            "total_price": item.total_price
        })
        
    return render_template(
        "order_confirmation.html",
        order=order,
        items=items_with_details,
        expected_delivery=expected_delivery
    )

@order_bp.route("/orders")
@login_required
def order_history():
    customer_id = session.get("customer_id")
    orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.order_date.desc()).all()
    return render_template("orders.html", orders=orders)

@order_bp.route("/orders/<order_id>")
def order_details(order_id):
    order = Order.query.filter_by(order_id=order_id).first_or_404()
    items_with_details = []
    for item in order.items:
        prod = Product.query.filter_by(product_id=item.product_id).first()
        items_with_details.append({
            "product_id": item.product_id,
            "name": prod.name if prod else item.product_id,
            "brand": prod.brand if prod else "",
            "category": prod.category if prod else "",
            "image_url": prod.image_url if prod else "",
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "discount": item.discount,
            "total_price": item.total_price
        })
        
    return render_template("order_details.html", order=order, items=items_with_details)

# API Endpoints
@order_bp.route("/api/orders", methods=["GET", "POST"])
def api_orders():
    if request.method == "POST":
        data = request.get_json() or {}
        customer_id = session.get("customer_id") or data.get("customer_id", "GUEST_CUST")
        cart = OrderService.get_or_create_cart(customer_id=customer_id)
        try:
            order = OrderService.place_order(customer_id, data, cart)
            return jsonify({"success": True, "order_id": order.order_id, "order": order.to_dict()}), 201
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400
            
    customer_id = session.get("customer_id")
    if not customer_id:
        return jsonify({"orders": []})
    orders = Order.query.filter_by(customer_id=customer_id).all()
    return jsonify({"orders": [o.to_dict() for o in orders]})

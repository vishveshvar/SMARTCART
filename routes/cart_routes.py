"""
SmartCart - Shopping Cart Routes & AJAX Operations
"""

import uuid
from flask import Blueprint, render_template, request, session, jsonify, flash, redirect, url_for
from database import db
from models import Cart, CartItem, Product
from services.order_service import OrderService

cart_bp = Blueprint("cart", __name__)

def _get_cart():
    customer_id = session.get("customer_id")
    session_id = session.get("cart_session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session["cart_session_id"] = session_id
        
    return OrderService.get_or_create_cart(customer_id=customer_id, session_id=session_id)

@cart_bp.route("/cart")
def view_cart():
    cart = _get_cart()
    cart_data = OrderService.get_cart_details(cart)
    return render_template("cart.html", cart=cart_data)

@cart_bp.route("/api/cart", methods=["GET"])
def api_get_cart():
    cart = _get_cart()
    cart_data = OrderService.get_cart_details(cart)
    return jsonify({"success": True, "cart": cart_data})

@cart_bp.route("/api/cart/add", methods=["POST"])
def api_add_to_cart():
    cart = _get_cart()
    data = request.get_json() or {}
    
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))
    bundle_pids = data.get("bundle_product_ids") # For 1-click Frequently Bought Together bundle
    
    items_to_add = bundle_pids if bundle_pids else ([product_id] if product_id else [])
    
    if not items_to_add:
        return jsonify({"success": False, "message": "No product specified"}), 400
        
    added_names = []
    for pid in items_to_add:
        product = Product.query.filter_by(product_id=pid).first()
        if not product:
            continue
            
        existing_item = CartItem.query.filter_by(cart_id=cart.id, product_id=pid).first()
        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = CartItem(cart_id=cart.id, product_id=pid, quantity=quantity)
            db.session.add(new_item)
        added_names.append(product.name)
        
    db.session.commit()
    cart_data = OrderService.get_cart_details(cart)
    
    msg = f"Added {len(items_to_add)} item(s) to your cart!" if len(items_to_add) > 1 else f"'{added_names[0]}' added to cart!"
    return jsonify({
        "success": True,
        "message": msg,
        "cart": cart_data,
        "total_items": cart_data["items_count"]
    })

@cart_bp.route("/api/cart/update", methods=["POST", "PUT"])
def api_update_cart():
    cart = _get_cart()
    data = request.get_json() or {}
    product_id = data.get("product_id")
    action = data.get("action") # 'increase', 'decrease', or direct 'quantity'
    quantity = data.get("quantity")
    
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if not item:
        return jsonify({"success": False, "message": "Item not in cart"}), 404
        
    if action == "increase":
        item.quantity += 1
    elif action == "decrease":
        item.quantity -= 1
        if item.quantity <= 0:
            db.session.delete(item)
    elif quantity is not None:
        qty = int(quantity)
        if qty <= 0:
            db.session.delete(item)
        else:
            item.quantity = qty
            
    db.session.commit()
    cart_data = OrderService.get_cart_details(cart)
    return jsonify({"success": True, "cart": cart_data})

@cart_bp.route("/api/cart/remove", methods=["POST", "DELETE"])
def api_remove_from_cart():
    cart = _get_cart()
    data = request.get_json() or {}
    product_id = data.get("product_id")
    
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        
    cart_data = OrderService.get_cart_details(cart)
    return jsonify({"success": True, "message": "Item removed from cart", "cart": cart_data})

@cart_bp.route("/api/cart/count", methods=["GET"])
def api_cart_count():
    cart = _get_cart()
    count = sum(item.quantity for item in cart.items)
    return jsonify({"count": count})

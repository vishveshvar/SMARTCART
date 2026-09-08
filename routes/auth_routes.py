"""
SmartCart - Authentication Routes
Handles user registration, login, logout, and role-based access control.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import db
from models import User, Customer

auth_bp = Blueprint("auth", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in as an administrator.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        if session.get("role") != "admin":
            flash("Access denied: Administrator privileges required.", "danger")
            return redirect(url_for("customer.home"))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["email"] = user.email
            session["role"] = user.role
            
            # If customer, store customer_id
            if user.customer:
                session["customer_id"] = user.customer.customer_id
                session["customer_name"] = user.customer.name
            else:
                session["customer_name"] = "Admin"
                
            flash(f"Welcome back, {session.get('customer_name')}!", "success")
            
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("customer.home"))
        else:
            flash("Invalid email or password. Please check your credentials.", "danger")
            
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        age = int(request.form.get("age", 25))
        gender = request.form.get("gender", "Other")
        city = request.form.get("city", "Mumbai")
        state = request.form.get("state", "Maharashtra")
        pref_cat = request.form.get("preferred_category", "Electronics")
        
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "warning")
            return render_template("register.html")
            
        # Create user
        new_user = User(email=email, role="customer")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()
        
        # Create customer profile
        cust_code = f"CUST_{Customer.query.count() + 1:05d}"
        new_customer = Customer(
            customer_id=cust_code,
            user_id=new_user.id,
            name=name,
            email=email,
            age=age,
            gender=gender,
            city=city,
            state=state,
            preferred_category=pref_cat,
            average_order_value=0.0,
            total_purchases=0
        )
        db.session.add(new_customer)
        db.session.commit()
        
        # Log in automatically
        session["user_id"] = new_user.id
        session["email"] = new_user.email
        session["role"] = new_user.role
        session["customer_id"] = cust_code
        session["customer_name"] = name
        
        flash("Registration successful! Welcome to SmartCart.", "success")
        return redirect(url_for("customer.home"))
        
    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("customer.home"))

# API Endpoints
@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session["user_id"] = user.id
        session["email"] = user.email
        session["role"] = user.role
        if user.customer:
            session["customer_id"] = user.customer.customer_id
            session["customer_name"] = user.customer.name
        return jsonify({"success": True, "user": user.to_dict()})
    return jsonify({"success": False, "message": "Invalid email or password"}), 401

@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already exists"}), 400
        
    user = User(email=email, role="customer")
    user.set_password(data.get("password", "Password@123"))
    db.session.add(user)
    db.session.flush()
    
    cust = Customer(
        customer_id=f"CUST_{Customer.query.count() + 1:05d}",
        user_id=user.id,
        name=data.get("name", "New Customer"),
        email=email,
        preferred_category=data.get("preferred_category", "Electronics")
    )
    db.session.add(cust)
    db.session.commit()
    return jsonify({"success": True, "customer_id": cust.customer_id})

@auth_bp.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

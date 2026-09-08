"""
SmartCart - Admin Management & Analytics Routes
Handles Admin Dashboard, 12-Chart Analytics, Recommendation Analytics,
ML Analytics, Product CRUD, Order Management, Customer Management,
Dataset Explorer with CSV Export, and Model Retraining.
"""

import os
import io
import csv
import json
import pandas as pd
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, send_file
from database import db
from models import Product, Customer, Order, OrderItem, RecommendationLog, Interaction, User
from services.analytics_service import AnalyticsService
from services.recommendation_service import recommendation_service
from train_model import train_and_evaluate, METRICS_FILE
from routes.auth_routes import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    kpis = AnalyticsService.get_dashboard_kpis()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(8).all()
    product_insights = AnalyticsService.get_product_insights()
    
    return render_template(
        "admin/dashboard.html",
        kpis=kpis,
        recent_orders=recent_orders,
        product_insights=product_insights
    )

@admin_bp.route("/analytics")
@admin_required
def analytics():
    kpis = AnalyticsService.get_dashboard_kpis()
    product_insights = AnalyticsService.get_product_insights()
    return render_template("admin/analytics.html", kpis=kpis, product_insights=product_insights)

@admin_bp.route("/api/analytics/charts")
@admin_required
def api_analytics_charts():
    charts_data = AnalyticsService.get_admin_charts_data()
    return jsonify(charts_data)

@admin_bp.route("/recommendations")
@admin_required
def recommendations():
    rec_stats = AnalyticsService.get_recommendation_kpis()
    return render_template("admin/recommendations.html", stats=rec_stats)

@admin_bp.route("/ml-analytics")
@admin_required
def ml_analytics():
    metrics = {}
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r") as f:
            metrics = json.load(f)
            
    return render_template("admin/ml_analytics.html", metrics=metrics)

@admin_bp.route("/retrain", methods=["POST"])
@admin_required
def retrain():
    try:
        new_metrics = train_and_evaluate()
        recommendation_service.reload()
        flash("AI Model retrained successfully! Metrics and weights updated.", "success")
    except Exception as e:
        flash(f"Error retraining model: {str(e)}", "danger")
    return redirect(url_for("admin.ml_analytics"))

@admin_bp.route("/api/retrain", methods=["POST"])
@admin_required
def api_retrain():
    try:
        new_metrics = train_and_evaluate()
        recommendation_service.reload()
        return jsonify({"success": True, "message": "Model retrained successfully", "metrics": new_metrics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/products", methods=["GET", "POST"])
@admin_required
def products():
    if request.method == "POST":
        action = request.form.get("action", "add")
        if action == "add":
            p_id = f"PROD_{Product.query.count() + 1:05d}"
            name = request.form.get("name")
            category = request.form.get("category")
            subcategory = request.form.get("subcategory", "")
            brand = request.form.get("brand", "")
            price = float(request.form.get("price", 999.0))
            discount = float(request.form.get("discount", 0.0))
            final_price = round(price * (1 - discount / 100), 2)
            stock = int(request.form.get("stock", 50))
            description = request.form.get("description", "")
            
            prod = Product(
                product_id=p_id,
                name=name,
                category=category,
                subcategory=subcategory,
                brand=brand,
                price=price,
                discount=discount,
                final_price=final_price,
                stock=stock,
                description=description,
                status="Active"
            )
            db.session.add(prod)
            db.session.commit()
            flash(f"Product '{name}' added successfully!", "success")
            
        elif action == "edit":
            p_id = request.form.get("product_id")
            prod = Product.query.filter_by(product_id=p_id).first()
            if prod:
                prod.name = request.form.get("name", prod.name)
                prod.category = request.form.get("category", prod.category)
                prod.subcategory = request.form.get("subcategory", prod.subcategory)
                prod.brand = request.form.get("brand", prod.brand)
                prod.price = float(request.form.get("price", prod.price))
                prod.discount = float(request.form.get("discount", prod.discount))
                prod.final_price = round(prod.price * (1 - prod.discount / 100), 2)
                prod.stock = int(request.form.get("stock", prod.stock))
                prod.rating = float(request.form.get("rating", prod.rating))
                prod.status = request.form.get("status", prod.status)
                db.session.commit()
                flash(f"Product '{prod.name}' updated!", "success")
                
        elif action == "delete":
            p_id = request.form.get("product_id")
            prod = Product.query.filter_by(product_id=p_id).first()
            if prod:
                prod.status = "Inactive" if prod.status == "Active" else "Active"
                db.session.commit()
                flash(f"Product status toggled for '{prod.name}'!", "info")
                
        return redirect(url_for("admin.products"))

    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "")
    query = Product.query
    if search_q:
        query = query.filter(Product.name.ilike(f"%{search_q}%") | Product.brand.ilike(f"%{search_q}%"))
        
    pagination = query.order_by(Product.id.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/products.html", products=pagination.items, pagination=pagination, search_q=search_q)

@admin_bp.route("/customers")
@admin_required
def customers():
    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "")
    query = Customer.query
    if search_q:
        query = query.filter(Customer.name.ilike(f"%{search_q}%") | Customer.customer_id.ilike(f"%{search_q}%"))
        
    pagination = query.order_by(Customer.id.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/customers.html", customers=pagination.items, pagination=pagination, search_q=search_q)

@admin_bp.route("/orders", methods=["GET", "POST"])
@admin_required
def orders():
    if request.method == "POST":
        order_id = request.form.get("order_id")
        new_status = request.form.get("status")
        order = Order.query.filter_by(order_id=order_id).first()
        if order and new_status in ["Placed", "Confirmed", "Packed", "Shipped", "Delivered", "Cancelled"]:
            order.status = new_status
            db.session.commit()
            flash(f"Order {order_id} status updated to '{new_status}'!", "success")
        return redirect(url_for("admin.orders"))

    status_filter = request.args.get("status")
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(Order.order_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/orders.html", orders=pagination.items, pagination=pagination, status_filter=status_filter)

@admin_bp.route("/dataset")
@admin_required
def dataset():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    stats = {
        "customers_count": Customer.query.count(),
        "products_count": Product.query.count(),
        "orders_count": Order.query.count(),
        "order_items_count": OrderItem.query.count(),
        "recommendations_count": RecommendationLog.query.count(),
        "interactions_csv_records": 0,
        "search_records": 0,
        "missing_values": 0,
        "duplicates": 0
    }
    
    sample_interactions = []
    int_csv = os.path.join(data_dir, "interactions.csv")
    if os.path.exists(int_csv):
        df_int = pd.read_csv(int_csv)
        stats["interactions_csv_records"] = len(df_int)
        stats["missing_values"] = int(df_int.isnull().sum().sum())
        stats["duplicates"] = int(df_int.duplicated().sum())
        sample_interactions = df_int.head(10).to_dict(orient="records")
        
    return render_template("admin/dataset.html", stats=stats, sample_interactions=sample_interactions)

@admin_bp.route("/dataset/export")
@admin_required
def export_dataset():
    """Generates and downloads a CSV export of system interactions or orders."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    int_csv = os.path.join(data_dir, "interactions.csv")
    
    if os.path.exists(int_csv):
        return send_file(
            int_csv,
            mimetype="text/csv",
            as_attachment=True,
            download_name="smartcart_interactions_export.csv"
        )
    else:
        # Generate on the fly from Order records
        orders = Order.query.all()
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(["Order_ID", "Customer_ID", "Order_Date", "Total_Amount", "Status", "Payment_Method"])
        for o in orders:
            cw.writerow([o.order_id, o.customer_id, o.order_date, o.total_amount, o.status, o.payment_method])
        output = io.BytesIO()
        output.write(si.getvalue().encode("utf-8"))
        output.seek(0)
        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name="smartcart_orders_export.csv"
        )

# System Architecture & Technical Design

This document details the software architecture, data flow, component interactions, and engineering patterns implemented in **SmartCart**.

---

## 1. High-Level Architecture

SmartCart adopts a modular multi-tier architecture separating client presentation, routing, business services, machine learning inference, and data persistence.

```mermaid
graph TD
    Client["Client Browser (Desktop / Mobile)<br/>HTML5, Bootstrap 5, Vanilla JS, Chart.js"]
    
    subgraph Presentation & Routing Layer [Flask 3.x Application]
        AuthRoutes["routes/auth_routes.py<br/>Login, Registration, Sessions"]
        CustRoutes["routes/customer_routes.py<br/>Home, Dashboard, Wishlist, Profile"]
        ProdRoutes["routes/product_routes.py<br/>Search, Filtering, Product Details"]
        CartRoutes["routes/cart_routes.py<br/>AJAX Cart Actions, Qty Stepper"]
        OrderRoutes["routes/order_routes.py<br/>Checkout, Tracking, Fulfillment"]
        RecRoutes["routes/recommendation_routes.py<br/>Rec APIs, Telemetry Tracking"]
        AdminRoutes["routes/admin_routes.py<br/>Dashboard, 12 Charts, ML Retraining, CRUD"]
    end

    subgraph Service & Machine Learning Layer
        RecService["services/recommendation_service.py<br/>Hybrid Multi-Factor Scoring & Fallback"]
        SimService["services/similarity_service.py<br/>TF-IDF & Cosine Similarity"]
        AssocService["services/association_service.py<br/>Order Co-occurrence & Bundles"]
        AnalyticsService["services/analytics_service.py<br/>12-Chart Metric Aggregations"]
        OrderService["services/order_service.py<br/>Cart Calculations & Stock Management"]
        
        MLModel["Random Forest Classifier (.pkl)<br/>Trained Propensity Estimator"]
        MLPipeline["Scikit-Learn Pipeline (.pkl)<br/>ColumnTransformer Scaler & OHE"]
    end

    subgraph Data & Storage Layer
        SQLAlchemy["Flask-SQLAlchemy ORM Engine"]
        MySQL["MySQL Database (smartcart_db)"]
        SQLite["SQLite Database (smartcart.db fallback)"]
        CSVStore["data/*.csv (32k+ Raw Interaction Records)"]
    end

    Client -->|HTTP / JSON Requests| Presentation
    Presentation -->|Delegates Logic| Service
    RecService -->|Inference Query| MLPipeline
    MLPipeline -->|Transformed Features| MLModel
    MLModel -->|Purchase Probability| RecService
    Service -->|Queries & Transactions| SQLAlchemy
    SQLAlchemy -->|PyMySQL Driver| MySQL
    SQLAlchemy -->|Local Engine| SQLite
    Service -->|Reads Reference Catalog| CSVStore
```

---

## 2. Request Lifecycle & Recommendation Sequence

When a customer visits the home page or product details page, the recommendation pipeline executes in sub-second time without expensive offline re-computations:

```mermaid
sequenceDiagram
    autonumber
    actor Customer as User / Browser
    participant Flask as Flask Route (customer_routes.py)
    participant RecServ as RecommendationService
    participant SimServ as SimilarityEngine
    participant AssocServ as AssociationEngine
    participant CacheML as Loaded Random Forest Model
    participant DB as Database (SQLAlchemy)

    Customer->>Flask: GET / or GET /product/PROD_00001
    Flask->>DB: Query customer profile, order history & wishlist
    DB-->>Flask: Customer demographics & past purchases
    
    par Personalized Recommendations
        Flask->>RecServ: get_personalized_recommendations(customer_data, history)
        RecServ->>CacheML: predict_proba(X_transformed)
        CacheML-->>RecServ: ML Purchase Probabilities
        RecServ->>RecServ: Apply Multi-Factor Scoring Formula
        RecServ-->>Flask: Top-N Ranked Products + XAI Reasons
    and Content Similarity
        Flask->>SimServ: get_similar_products(product_id, top_n=6)
        SimServ-->>Flask: Top-6 Cosine Similar Products
    and Market Basket Bundle
        Flask->>AssocServ: get_frequently_bought_together(product_id)
        AssocServ-->>Flask: Co-occurrence Bundle + 10% Discount
    end

    Flask->>DB: Log recommendation impression (RecommendationLog)
    Flask-->>Customer: Render HTML with dynamic cards, badges & bundles
    Customer->>Flask: Click Recommended Card (POST /api/recommendations/track)
    Flask->>DB: Update RecommendationLog (clicked = 1)
```

---

## 3. Component Responsibilities

### 1. Application Controller (`app.py`)
- Initializes Flask with configuration loaded from `config.py`.
- Mounts 7 modular blueprints (`auth_bp`, `customer_bp`, `product_bp`, `cart_bp`, `order_bp`, `recommendation_bp`, `admin_bp`).
- Context processor automatically injects active cart item counts, wishlist badge numbers, and category navigation lists into all templates.
- Configures custom error pages (404 Not Found, 500 Internal Error) without leaking sensitive stack traces.

### 2. Service Layer (`services/`)
- **`recommendation_service.py`**: Singleton engine keeping the serialized Random Forest model and preprocessor pipeline in memory for sub-second vector inference. Combines model purchase propensity with category preference, popularity, and ratings.
- **`similarity_service.py`**: Computes pairwise cosine similarities across product descriptions, tags, brands, and subcategories using TF-IDF.
- **`association_service.py`**: Parses multi-item transactions to build co-occurrence frequency matrices for Frequently Bought Together bundle generation.
- **`analytics_service.py`**: Extracts real-time KPI metrics, interaction funnels, conversion rates, and 14-day sales trends for Chart.js.
- **`order_service.py`**: Calculates cart subtotals, item-level discounts, delivery thresholds, handles order insertion, and decrements product inventory atomically.

### 3. Client Layer (`static/` & `templates/`)
- Pure HTML5 + Jinja2 templating with Bootstrap 5.3 framework.
- Theme switching mechanism storing dark/light mode preference in `localStorage`.
- Asynchronous JavaScript (`fetch` API) for non-blocking add-to-cart, quantity changes, live search suggestions, and telemetry tracking.

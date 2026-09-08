# REST API Reference Documentation

This document provides technical documentation for all HTTP API endpoints implemented in **SmartCart**.

---

## Base URL
All relative paths are served from `http://127.0.0.1:5000/`.

---

## 1. Authentication Endpoints

### `POST /api/login`
Authenticates user credentials and establishes a signed session cookie.

- **Request Body (`application/json`)**:
  ```json
  {
    "email": "customer@smartcart.com",
    "password": "Customer@123"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "success": true,
      "user": {
        "id": 2,
        "email": "customer@smartcart.com",
        "role": "customer",
        "created_at": "2026-09-08 18:17:30"
      }
    }
    ```
  - `401 Unauthorized`:
    ```json
    {
      "success": false,
      "message": "Invalid email or password"
    }
    ```

---

### `POST /api/register`
Registers a new customer account and creates a linked demographic profile.

- **Request Body (`application/json`)**:
  ```json
  {
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "password": "PriyaPassword@123",
    "preferred_category": "Electronics"
  }
  ```
- **Responses**:
  - `200 OK`: `{"success": true, "customer_id": "CUST_03001"}`
  - `400 Bad Request`: `{"success": false, "message": "Email already exists"}`

---

### `POST /api/logout`
Clears session cookies and terminates the active session.

- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "message": "Logged out successfully"
  }
  ```

---

## 2. Product & Search Endpoints

### `GET /api/products`
Retrieves paginated catalog products with optional category filtering.

- **Query Parameters**:
  - `page` (integer, default: 1)
  - `limit` (integer, default: 20)
  - `category` (string, optional)
- **Response `200 OK`**:
  ```json
  {
    "page": 1,
    "total": 630,
    "products": [
      {
        "id": 1,
        "product_id": "PROD_00001",
        "name": "Sony Wireless Bluetooth Headphones",
        "category": "Electronics",
        "subcategory": "Audio",
        "brand": "Sony",
        "price": 4500.0,
        "discount": 20.0,
        "final_price": 3600.0,
        "rating": 4.6,
        "review_count": 342,
        "stock": 85,
        "popularity_score": 88.5,
        "status": "Active"
      }
    ]
  }
  ```

---

### `GET /api/products/<product_id>`
Fetches detailed product specifications by unique alphanumeric ID.

- **Example**: `GET /api/products/PROD_00001`
- **Response `200 OK`**: Single product JSON object.
- **Response `404 Not Found`**: `{"error": "Product not found"}`

---

### `GET /api/search/suggestions`
Provides live autocomplete suggestions matching query substrings.

- **Query Parameters**:
  - `q` (string, minimum 2 characters)
- **Example**: `GET /api/search/suggestions?q=headphone`
- **Response `200 OK`**:
  ```json
  [
    {
      "id": "PROD_00001",
      "name": "Sony Wireless Bluetooth Headphones",
      "brand": "Sony",
      "category": "Electronics",
      "price": 3600.0,
      "image_url": "https://images.unsplash.com/..."
    }
  ]
  ```

---

## 3. Recommendation Endpoints

### `GET /api/recommendations`
Returns personalized recommendations for the authenticated customer based on Random Forest purchase probability and multi-factor scoring.

- **Query Parameters**:
  - `limit` (integer, default: 8)
- **Response `200 OK`**:
  ```json
  {
    "count": 8,
    "success": true,
    "recommendations": [
      {
        "Product_ID": "PROD_00012",
        "Product_Name": "Bose Compact Bluetooth Speaker",
        "Category": "Electronics",
        "Final_Price": 4999.0,
        "Rating": 4.7,
        "match_percentage": 94,
        "badge_label": "AI Recommended",
        "recommendation_reason": "Matches your shopping preference for Electronics."
      }
    ]
  }
  ```

---

### `GET /api/recommendations/similar/<product_id>`
Returns top similar products computed via TF-IDF vectorization and Cosine Similarity.

- **Query Parameters**: `limit` (default: 6)
- **Response `200 OK`**:
  ```json
  {
    "product_id": "PROD_00001",
    "success": true,
    "similar_products": [
      {
        "Product_ID": "PROD_00005",
        "Product_Name": "JBL Noise Cancelling Earbuds",
        "similarity_score": 84.5,
        "Final_Price": 2999.0
      }
    ]
  }
  ```

---

### `GET /api/recommendations/frequently-bought/<product_id>`
Returns primary product bundle items computed from historical order co-occurrence with 10% bundle discount pricing.

- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "bundle": {
      "primary_product": { "Product_ID": "PROD_00001", "Final_Price": 3600.0 },
      "bundle_items": [
        { "Product_ID": "PROD_00450", "Product_Name": "Protective Headphone Case", "Final_Price": 499.0 }
      ],
      "original_bundle_price": 4099.0,
      "extra_bundle_discount": 409.9,
      "total_bundle_price": 3689.1,
      "total_savings": 819.9
    }
  }
  ```

---

### `POST /api/recommendations/track`
Logs customer interactions with recommendation cards to compute Recommendation CTR and CVR.

- **Request Body**:
  ```json
  {
    "product_id": "PROD_00012",
    "event_type": "click",
    "recommendation_type": "Personalized"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "message": "Tracked click"
  }
  ```

---

## 4. Shopping Cart Endpoints

### `GET /api/cart`
Returns active shopping cart contents, line item calculations, delivery fee, and grand total.

- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "cart": {
      "items": [
        {
          "cart_item_id": 1,
          "product_id": "PROD_00001",
          "name": "Sony Wireless Headphones",
          "quantity": 2,
          "final_price": 3600.0,
          "item_final": 7200.0
        }
      ],
      "items_count": 2,
      "subtotal": 9000.0,
      "total_discount": 1800.0,
      "delivery_fee": 0.0,
      "grand_total": 7200.0
    }
  }
  ```

---

### `POST /api/cart/add`
Adds a product or multiple bundle items to the cart.

- **Single Product Payload**: `{"product_id": "PROD_00001", "quantity": 1}`
- **Bundle Payload**: `{"bundle_product_ids": ["PROD_00001", "PROD_00450"], "quantity": 1}`
- **Response `200 OK`**: `{"success": true, "message": "Added to cart", "total_items": 3}`

---

### `POST /api/cart/update`
Modifies item quantity (`increase` or `decrease`).

- **Request Body**:
  ```json
  {
    "product_id": "PROD_00001",
    "action": "increase"
  }
  ```
- **Response `200 OK`**: Updated cart dictionary.

---

### `POST /api/cart/remove`
Removes an item completely from the cart.

- **Request Body**: `{"product_id": "PROD_00001"}`
- **Response `200 OK`**: `{"success": true, "message": "Item removed from cart"}`

---

## 5. Admin & Analytics Endpoints

### `GET /admin/api/analytics/charts`
*(Protected: Requires `admin` session)*
Returns real database aggregated timeseries and distributions for all 12 Chart.js analytics graphs.

- **Key JSON Response Fields**:
  - `daily_sales`: 14-day revenue timeseries `{labels: [...], data: [...]}`
  - `monthly_revenue`: Trailing 6-month revenues
  - `orders_over_time`: Daily order counts
  - `sales_by_category`: Revenue breakdown by product category
  - `top_products`: Top 5 bestselling products (units & revenue)
  - `customer_growth`: Monthly new customer registration counts
  - `funnel`: Interaction funnel counts `[views, wishlists, carts, purchases]`
  - `cart_rate`: Add-to-cart rate percentage
  - `conversion_rate`: Order conversion rate percentage
  - `rec_ctr`: Recommendation Click-Through Rate (%)
  - `rec_cvr`: Recommendation Conversion Rate (%)
  - `daily_aov`: Daily Average Order Value trend

---

### `POST /api/retrain`
*(Protected: Requires `admin` session)*
Triggers model retraining, preprocessor refitting, evaluation metrics calculation, and memory reloading.

- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "message": "Model retrained successfully",
    "metrics": {
      "model_name": "Random Forest Classifier",
      "accuracy": 0.7858,
      "precision": 0.3892,
      "recall": 0.9954,
      "f1_score": 0.5596,
      "roc_auc": 0.8696
    }
  }
  ```

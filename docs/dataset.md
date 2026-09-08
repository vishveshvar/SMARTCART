# Dataset Documentation & Data Generation

This document details the synthetic data generation methodology, schema definitions, and behavioral modeling implemented in **SmartCart**.

---

## 1. Generation Overview

To ensure complete independence from third-party or proprietary datasets, SmartCart incorporates an autonomous dataset generation pipeline (`generate_dataset.py`).

The generator synthesizes realistic consumer browsing, searching, carting, and purchasing dynamics across **15 distinct retail categories** using parameterized distributions (Gaussian, Poisson, and Exponential) and reproducible random seeds (`random.seed(42)` and `numpy.random.seed(42)`).

```
   [ Customer Demographics ]      [ Product Specifications ]
   (3,000 synthetic profiles)     (630 catalog items in 15 cats)
               │                                │
               └───────────────┬────────────────┘
                               ▼
            [ Behavioral Interaction Generator ]
         (Views, Searches, Wishlists, Carts, Orders)
                               │
       ┌───────────────┬───────┴───────┬───────────────┐
       ▼               ▼               ▼               ▼
interactions.csv  purchases.csv  search_history.csv  ratings.csv
 (32,003 rows)    (3,060 rows)      (5,638 rows)     (1,313 rows)
```

---

## 2. Dataset Metrics Summary

All dataset files reside under `data/`:

| Dataset File | Exact Records | Size on Disk | Primary Key / Unique ID |
| :--- | :---: | :---: | :--- |
| `data/products.csv` | **630** | ~273 KB | `Product_ID` (e.g. `PROD_00001`) |
| `data/customers.csv` | **3,000** | ~305 KB | `Customer_ID` (e.g. `CUST_00001`) |
| `data/interactions.csv` | **32,003** | ~3.4 MB | `Interaction_ID` (e.g. `INT_0000001`) |
| `data/purchases.csv` | **3,060** | ~357 KB | `Purchase_ID` (e.g. `PUR_000001`) |
| `data/search_history.csv` | **5,638** | ~641 KB | `Search_ID` (e.g. `SRCH_000001`) |
| `data/ratings.csv` | **1,313** | ~124 KB | `Rating_ID` (e.g. `RAT_000001`) |

---

## 3. Data Dictionary & Schemas

### 1. Products (`data/products.csv`)

| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :---: | :--- | :--- |
| `Product_ID` | String | No | Unique product identifier | `PROD_00001` |
| `Product_Name` | String | No | Full commercial product name | `Sony Wireless Bluetooth Headphones` |
| `Category` | String | No | Top-level category (15 retail types) | `Electronics` |
| `Subcategory` | String | Yes | Specific sub-department | `Audio` |
| `Brand` | String | Yes | Manufacturing brand | `Sony` |
| `Price` | Float | No | Base retail MRP in INR (₹) | `4500.0` |
| `Discount` | Float | No | Percentage discount (0–50%) | `20.0` |
| `Final_Price` | Float | No | Discounted price paid by customer | `3600.0` |
| `Rating` | Float | No | Average star rating (3.5–5.0) | `4.6` |
| `Review_Count` | Integer | No | Count of verified reviews | `342` |
| `Stock` | Integer | No | Available warehouse inventory | `85` |
| `Popularity_Score` | Float | No | Composite popularity index (0–100) | `88.5` |
| `Product_Description` | Text | Yes | Editorial product description | `Over-ear noise cancelling headphones...` |
| `Product_Tags` | String | Yes | Comma-separated search tokens | `wireless,bluetooth,audio,sony` |
| `Age_Group` | String | No | Target age bracket | `18-35` |
| `Gender_Target` | String | No | Target demographic | `All` |
| `Color` | String | No | Variant colorway | `Midnight Black` |
| `Size` | String | No | Variant dimension/capacity | `Standard` |
| `Created_Date` | Date | No | Catalog onboarding date | `2025-08-14` |
| `Image_URL` | String | Yes | Visual placeholder image URI | `https://images.unsplash.com/...` |
| `Status` | String | No | Active or Inactive catalog status | `Active` |

### 2. Customers (`data/customers.csv`)

| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :---: | :--- | :--- |
| `Customer_ID` | String | No | Unique customer identifier | `CUST_00001` |
| `Customer_Name` | String | No | Full customer name | `Aarav Sharma` |
| `Age` | Integer | No | Customer age in years (18–70) | `28` |
| `Gender` | String | No | Declared gender | `Male` |
| `City` | String | No | Customer home city | `Bengaluru` |
| `State` | String | No | Customer home state | `Karnataka` |
| `Registration_Date` | Date | No | User account creation date | `2025-02-11` |
| `Preferred_Category` | String | No | Stated primary shopping category | `Electronics` |
| `Average_Order_Value` | Float | No | Historical average spend in INR | `4500.0` |
| `Total_Purchases` | Integer | No | Historical total orders placed | `8` |
| `Purchase_Frequency` | Float | No | Orders per month | `1.2` |
| `Average_Rating_Given` | Float | No | Mean rating given by customer | `4.8` |
| `Last_Purchase_Date` | Date | Yes | Timestamp of most recent order | `2026-08-25` |

### 3. Customer Interactions (`data/interactions.csv`)

| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :---: | :--- | :--- |
| `Interaction_ID` | String | No | Unique interaction telemetry ID | `INT_0000001` |
| `Customer_ID` | String | No | Linked customer ID | `CUST_00042` |
| `Product_ID` | String | No | Linked product ID | `PROD_00105` |
| `Interaction_Type` | String | No | Action: `View`, `Search`, `Wishlist`, `Cart`, `Purchase`, `Rating` | `View` |
| `Timestamp` | DateTime | No | Telemetry event timestamp | `2026-06-14 14:32:10` |
| `Session_ID` | String | No | Browser session token | `SESS_492014` |
| `Search_Keyword` | String | Yes | Associated search token | `headphones` |
| `Category` | String | No | Product category | `Electronics` |
| `Device` | String | No | `Mobile App`, `Mobile Web`, `Desktop`, `Tablet` | `Mobile App` |
| `Time_Spent` | Integer | No | Time on product page in seconds | `75` |
| `Product_Viewed` | Integer | No | Binary flag: 1 if viewed | `1` |
| `Added_To_Wishlist` | Integer | No | Binary flag: 1 if wishlisted | `0` |
| `Added_To_Cart` | Integer | No | Binary flag: 1 if added to cart | `1` |
| `Purchased` | Integer | No | Target variable: 1 if purchased | `1` |
| `Rating_Given` | Integer | No | Rating given if reviewed (0 if none) | `5` |

### 4. Purchases (`data/purchases.csv`)

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `Purchase_ID` | String | Unique purchase record identifier (`PUR_000001`) |
| `Customer_ID` | String | Buyer customer identifier |
| `Product_ID` | String | Purchased item identifier |
| `Order_ID` | String | Multi-item checkout grouping token (`SC-2026-001045`) |
| `Purchase_Date` | DateTime | Transaction timestamp |
| `Quantity` | Integer | Item units ordered |
| `Unit_Price` | Float | Base product price before discount |
| `Discount` | Float | Percentage discount applied |
| `Total_Amount` | Float | Net amount paid for this line item |
| `Payment_Method` | String | `UPI`, `Credit Card`, `Debit Card`, `Net Banking`, `Cash on Delivery`, `Wallet` |
| `Category` | String | Product category |
| `Device` | String | Checkout device used |

### 5. Search History (`data/search_history.csv`)

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `Search_ID` | String | Unique search session event identifier (`SRCH_000001`) |
| `Customer_ID` | String | Searching customer identifier |
| `Search_Keyword` | String | Query term entered (e.g. `wireless earbuds`, `gaming laptop`) |
| `Search_Category` | String | Detected or filtered retail category |
| `Search_Date` | DateTime | Query execution timestamp |
| `Result_Clicked` | Integer | Binary flag: 1 if user selected a suggested result |
| `Product_Clicked` | String | Name of product selected from results |

### 6. Ratings (`data/ratings.csv`)

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `Rating_ID` | String | Unique review identifier (`RAT_000001`) |
| `Customer_ID` | String | Author customer identifier |
| `Product_ID` | String | Reviewed product identifier |
| `Rating` | Integer | Integer rating score from 1 to 5 |
| `Review_Text` | Text | Written qualitative customer review |
| `Rating_Date` | DateTime | Review submission timestamp |

---

## 4. Behavioral Modeling Rules

The synthetic data generation incorporates realistic statistical correlations:

1. **Age-Based Preference Weighting**:
   - `Age <= 28`: 5x higher probability weight towards `Electronics`, `Gaming`, `Mobiles`, and `Footwear`.
   - `Age 29-45`: Affinity distributed towards `Laptops`, `Home`, `Kitchen`, and `Personal Care`.
   - `Age > 45`: Affinity distributed towards `Home`, `Furniture`, `Kitchen`, `Books`, and `Grocery`.

2. **Conversion Funnel Probability Chain**:
   $$\text{Session} \xrightarrow{P(\text{Search})} \text{Search} \xrightarrow{P(\text{View})=1.0} \text{View} \xrightarrow{P(\text{Wish})=0.22} \text{Wishlist} \xrightarrow{P(\text{Cart})=0.35} \text{Cart} \xrightarrow{P(\text{Buy})=0.58} \text{Order}$$

3. **Complementary Basket Co-occurrence**:
   When a customer buys a primary item, complementary items are bundled into identical `Order_ID` groups with a 65% probability:
   - `Laptops` $\rightarrow$ `Accessories` (Laptop Bag, Wireless Mouse) or `Gaming` (Keyboards).
   - `Mobiles` $\rightarrow$ `Accessories` (Phone Case, Screen Protector, Wireless Charger).
   - `Footwear` $\rightarrow$ `Fashion` (Socks, Joggers, Chinos).
   - `Cookware` $\rightarrow$ `Kitchen Tools` (Stainless Steel Chef Knives, Food Jars).

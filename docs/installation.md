# Installation & Setup Guide

This guide provides end-to-end instructions for installing, configuring, and deploying **SmartCart** locally across Windows, Linux, and macOS environments.

---

## 1. Prerequisites

- **Python**: Version 3.10 or newer (tested on Python 3.14).
- **Git**: For cloning the repository and managing version control.
- **Database Engine** (Optional):
  - **SQLite**: Built into Python; no external server installation required.
  - **MySQL**: Version 8.0+ if using a dedicated relational database server.

---

## 2. Clone the Repository

```bash
git clone https://github.com/vishveshvar/SMARTCART.git
cd SMARTCART
```

---

## 3. Set Up a Virtual Environment

Isolate project dependencies within a virtual environment:

### Windows (PowerShell / Command Prompt):
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Install Dependencies

Install all core dependencies using pip:
```bash
pip install -r requirements.txt
```

### Core Packages Installed:
- `Flask>=3.0.0`: Core WSGI web application framework
- `Flask-SQLAlchemy>=3.1.0`: ORM integration
- `PyMySQL>=1.1.0`: Pure Python MySQL client
- `scikit-learn>=1.3.0`: Random Forest classifier & transformers
- `pandas>=2.0.0`: DataFrames & tabular manipulations
- `numpy>=1.24.0`: Numerical calculations & vector operations
- `joblib>=1.3.0`: Model serialization
- `Werkzeug>=3.0.0`: Secure password hashing & utilities

---

## 5. Configure Environment Variables (Optional)

Copy the sample environment file:
```bash
# Windows:
copy .env.example .env

# Linux / macOS:
cp .env.example .env
```

### Supported Configuration Keys:
- `SECRET_KEY`: Session encryption secret (default: fallback development key).
- `USE_SQLITE`: Set to `true` to force SQLite mode (`smartcart.db`).
- `DATABASE_URL`: Complete database connection string (e.g., `mysql+pymysql://root:password@localhost:3306/smartcart_db`).
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`: MySQL connection parameters.

> **Note**: If no environment variables are set, SmartCart defaults to local SQLite (`smartcart.db`), running with zero manual database setup.

---

## 6. (Optional) Setup MySQL Server

If using MySQL instead of the default SQLite engine:

1. Log into your MySQL console:
   ```bash
   mysql -u root -p
   ```
2. Create the database and tables using the provided schema:
   ```sql
   CREATE DATABASE smartcart_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```
3. Execute the schema script:
   ```bash
   mysql -u root -p smartcart_db < schema.sql
   ```
4. Set `DATABASE_URL` in your `.env` or system environment:
   ```bash
   export DATABASE_URL="mysql+pymysql://root:password@localhost:3306/smartcart_db"
   ```

---

## 7. Generate Datasets & Train Model

If you are setting up from scratch without pre-existing datasets:

### 1. Generate Synthetic Datasets:
```bash
python generate_dataset.py
```
*Generates 6 CSV files with 32,000+ interaction records in `data/`.*

### 2. Train the Random Forest Model:
```bash
python train_model.py
```
*Fits preprocessing pipeline and Random Forest classifier, producing evaluation metrics and saving artifacts to `models/`.*

### 3. Initialize & Seed Database:
```bash
python seed_db.py
```
*Populates tables with products, customer demographics, historical orders, and initializes demo accounts.*

---

## 8. Run the Application

Start the Flask development server:
```bash
python app.py
```

Console Output:
```
RecommendationService: Loaded Random Forest model and preprocessor pipeline.
RecommendationService: Loaded 630 products for catalog.
SimilarityEngine: Fitted cosine similarity on 630 products.
AssociationEngine: Analyzed 2655 orders for co-occurrence associations.
=== SmartCart Server Starting on http://127.0.0.1:5000 ===
 * Running on http://127.0.0.1:5000
```

Access the application in your browser at:
**`http://127.0.0.1:5000`**

---

## 9. Run the Test Suite

Execute the automated test suite verifying all 12 subsystems:
```bash
python -m unittest tests/test_smartcart.py
```
Expected output:
```
Ran 12 tests in 2.297s
OK
```

---

## 10. Troubleshooting

### Port 5000 Already in Use
Specify an alternate port in `app.py` or run via Flask CLI:
```bash
flask run --port 5001
```

### ModuleNotFoundError
Ensure your virtual environment is active and dependencies are installed:
```bash
pip install -r requirements.txt
```

### MySQL Connection Refused
Ensure your MySQL server daemon is running:
- **Windows**: `Start-Service MySQL` (or via Services GUI).
- **Linux**: `sudo systemctl start mysql`
- Alternatively, leave `USE_SQLITE=true` to use the built-in SQLite engine.

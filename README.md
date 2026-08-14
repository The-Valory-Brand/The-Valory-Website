# 💎 THE VALORY — Premium Full-Stack E-Commerce Platform

[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-4.2%2B-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](#-license--copyright)

**THE VALORY** ("Timeless Elegance") is a production-ready, high-fashion e-commerce platform built for Tamil Nadu, India. The application features a modular Django backend, PostgreSQL database, custom luxury noir & cream UI design system, cryptographically secure OTP & Google OAuth authentication, strict Role-Based Access Control (RBAC), real-time inventory controls, verified damaged-product refund workflow, customer notifications, audit logging, and financial analytics exporters.

---

## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [📦 System Architecture & Modular Apps](#-system-architecture--modular-apps)
- [🔒 Role-Based Access Control (RBAC)](#-role-based-access-control-rbac)
- [💎 Business & Regional Logistics Policies](#-business--regional-logistics-policies)
- [🛠️ Technology Stack](#-technology-stack)
- [⚙️ Environment Variables](#️-environment-variables)
- [🚀 Local Installation & Setup](#-local-installation--setup)
- [🧪 Running Automated Tests](#-running-automated-tests)
- [🌐 Render Deployment Guide](#-render-deployment-guide)
- [📜 License & Copyright](#-license--copyright)

---

## ✨ Key Features

- **Luxury Noir/Cream Aesthetics:** Custom aesthetic design system built with CSS custom properties, responsive navigation, sticky micro-interactions, modal size pickers, dynamic hero sliders, and smooth cart drawer transitions.
- **Secure Multi-Factor Authentication:** Email & password authentication with hashed 6-digit OTP verification for account activation, password resets, and Google OAuth integration.
- **Strict Role-Based Access Control (RBAC):** Three distinct user roles—*Main Admin*, *Operational Manager*, and *Customer*—enforced via database flags and custom Django view decorators (`@main_admin_required`, `@manager_required`).
- **Catalog & Size Inventory Management:** Full CRUD operations for clothing categories, products, images, and size-specific stock tracking (S, M, L, XL, XXL) with concurrency guards.
- **Cart & Order Lifecycle Management:** Session-persistent shopping cart context processor, coupon code application, checkout state machine (`Placed` → `Payment Confirmed` → `Processing` → `Packed` → `Dispatched` → `Delivered`), and strict pre-dispatch order cancellation with instant atomic stock restoration.
- **24-Hour Damaged Product Refund Workflow:** Dedicated refund portal requiring unboxing video link/upload and photographic proof within 24 hours of delivery. Refunds are verified and audited by staff before approval.
- **Exclusive Financial Analytics & Export:** Dedicated dashboard for Main Admin featuring total revenue breakdown, monthly refund statistics, audit activity logs, and one-click CSV report exports.
- **Customer Notifications & Audit Logs:** In-app notification center for real-time order state changes and audit logging of staff actions.

---

## 📦 System Architecture & Modular Apps

The codebase follows a modular Django app architecture under the `apps/` directory:

```text
The Valory Website/
├── apps/
│   ├── accounts/         # Custom User model, OTP generation, auth views, RBAC decorators
│   ├── audit/            # Audit logging system for operational and status changes
│   ├── cart/             # Shopping cart context processor, session handling, coupon codes
│   ├── notifications/    # In-app user & manager notification center
│   ├── orders/           # Order creation, status state machine, cancellation logic
│   ├── payments/         # Payment verification & method processing (Razorpay, COD)
│   ├── policies/         # Terms of Service, Privacy Policy, Return & Shipping policies
│   ├── products/         # Product catalog, categories, size variants, database seeding
│   ├── refunds/          # Unboxing video & photo damaged refund workflow
│   ├── reports/          # Admin-exclusive financial analytics & CSV exporter
│   └── reviews/          # Verified customer reviews and rating system
├── config/               # Django core configuration (settings, urls, wsgi, asgi)
├── static/               # CSS stylesheets, JavaScript modules, brand assets
├── templates/            # HTML5 semantic templates & components
├── build.sh              # Production build script for static assets & migrations
├── render.yaml           # Infrastructure-as-code spec for Render deployment
└── manage.py             # Django management entry point
```

---

## 🔒 Role-Based Access Control (RBAC)

Access permissions are enforced strictly at the database, decorator, and view levels:

| Feature / Workspace Area | Main Admin | Operational Manager | Customer |
| :--- | :---: | :---: | :---: |
| Storefront Browsing, Cart & Checkout | ✅ Yes | ✅ Yes | ✅ Yes |
| Product & Size Inventory Management (CRUD) | ✅ Yes | ✅ Yes | ❌ Blocked |
| Category Management (CRUD) | ✅ Yes | ✅ Yes | ❌ Blocked |
| Order Processing (`Placed` → `Dispatched`) | ✅ Yes | ✅ Yes | ❌ Blocked |
| Pre-Dispatch Customer Order Cancellation | ✅ Yes | ✅ Yes | ✅ Own Pre-Dispatch Orders |
| Damaged Product Refund Approvals | ✅ Yes | ✅ Yes | ❌ Blocked (Can submit own) |
| **Financial Revenue & Sales Analytics** | **✅ YES (Exclusive)** | ⛔ HTTP 403 Forbidden | ⛔ HTTP 403 Forbidden |
| **Monthly Refund & Return Analytics** | **✅ YES (Exclusive)** | ⛔ HTTP 403 Forbidden | ⛔ HTTP 403 Forbidden |
| **Manager Account Provisioning (CRUD)** | **✅ YES (Exclusive)** | ⛔ HTTP 403 Forbidden | ⛔ HTTP 403 Forbidden |
| **Financial CSV Report Exporters** | **✅ YES (Exclusive)** | ⛔ HTTP 403 Forbidden | ⛔ HTTP 403 Forbidden |

---

## 💎 Business & Regional Logistics Policies

1. **Tamil Nadu Logistics Focus:** Express delivery across all major cities and districts in Tamil Nadu, India (Chennai, Coimbatore, Madurai, Tiruchirappalli, Salem, Erode, etc.).
2. **Strict No-Return / No-Exchange Policy:** General returns or size exchanges are **not permitted**. Size charts (S, M, L, XL, XXL) are provided on each product page for accuracy.
3. **Damaged Product Refund Exemption:** Refunds are granted **strictly** for verified damaged items. Customers must submit photo proof and an unboxing video within **24 hours** of order delivery.
4. **Pre-Dispatch Order Cancellation:** Cancellation is permitted strictly **before dispatch** (while order status is `Placed`, `Payment Confirmed`, `Processing`, or `Packed`). Once an order status becomes `DISPATCHED`, cancellation is blocked server-side. Pre-dispatch cancellation automatically restores product inventory.

---

## 🛠️ Technology Stack

- **Backend Framework:** Python 3.12+, Django 4.2+ (Modular App Pattern, ORM, Auth Framework, Email Backend)
- **Database Engine:** PostgreSQL (`psycopg2-binary`, `dj-database-url`) with SQLite fallback for local development
- **Production Web Server:** Gunicorn WSGI, WhiteNoise static file compression
- **Frontend Stack:** HTML5 Semantic Markup, Custom Vanilla CSS (Luxury Noir/Cream design system), Vanilla JavaScript ES6
- **Security Protocols:** CSRF Tokens, XSS Filtering, SQL Injection Prevention, Argon2/PBKDF2 Password Hashing, Hashed OTPs with rate-limiting, SSL/TLS Redirects in production
- **Deployment Platform:** Render (Web Service + Managed PostgreSQL Database)

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and set the following parameters:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | `django-insecure-...` | Django secret key (Must be changed in production) |
| `DEBUG` | `True` | Debug flag (`True` for local dev, `False` for production) |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,.onrender.com` | Comma-separated list of permitted host headers |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:8000,...` | Trusted origins for CSRF POST requests |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Database connection URI (PostgreSQL in production) |
| `EMAIL_BACKEND` | `...console.EmailBackend` | Django email backend (`smtp.EmailBackend` for production) |
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP host server |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_USE_TLS` | `True` | TLS encryption flag |
| `EMAIL_HOST_USER` | `""` | SMTP authentication username / sender email |
| `EMAIL_HOST_PASSWORD` | `""` | SMTP application password |
| `GOOGLE_CLIENT_ID` | `""` | Google OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | `""` | Google OAuth 2.0 Client Secret |
| `OTP_EXPIRY_MINUTES` | `10` | Expiration window for 6-digit OTP codes |
| `OTP_RESEND_COOLDOWN_SECONDS` | `60` | Cooldown period between OTP resend requests |

---

## 🚀 Local Installation & Setup

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/your-username/the-valory.git
cd "The Valory Website"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell / CMD):
.\venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment File
```bash
cp .env.example .env
```

### 3. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Seed Product Catalog & Sample Data
```bash
python manage.py seed_data
```

### 5. Create Main Admin Superuser
```bash
python manage.py createsuperuser
```

### 6. Start Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Automated Tests

To run the complete Django test suite covering RBAC access controls, OTP workflows, inventory stock updates, and order cancellation logic:

```bash
python manage.py test apps
```

---

## 🌐 Render Deployment Guide

The repository includes pre-configured `render.yaml` and `build.sh` files for one-click deployment on Render.

1. **Push Code to GitHub:** Ensure your repository is updated on GitHub.
2. **Connect to Render:** Log into [Render Dashboard](https://dashboard.render.com/) and click **New > Blueprint**.
3. **Select Repository:** Connect your repository containing `render.yaml`. Render will automatically create:
   - A **Python Web Service** (`the-valory-web`)
   - A **PostgreSQL Database** (`the-valory-db`)
4. **Environment Variables:** Set production environment variables in Render:
   - `DEBUG=False`
   - `SECRET_KEY=your-secure-production-key`
   - `ALLOWED_HOSTS=.onrender.com,your-custom-domain.com`
   - `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`
   - `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` (for live OTP / transaction emails)
5. **Automatic Build Execution:** The `./build.sh` script automatically installs dependencies, collects static files via WhiteNoise, runs migrations, and seeds catalog data if empty.

---

## 📜 License & Copyright

&copy; 2026 **THE VALORY**. All Rights Reserved. Timeless Elegance.


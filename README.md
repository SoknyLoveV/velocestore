# VeloceStore - Flask Ecommerce Store

A complete, production-quality, responsive E-commerce Web Application built with Python **Flask** framework, **Jinja2** templating engine, **Bootstrap 5**, and integrated dynamically with the **FakeStore API**. 

The app features a cookie-based cart system, session-backed user authentication, support contact forms, order dispatch notifications via **Telegram Bot API**, and a modern aesthetic with indigo/violet gradients and glassmorphism styling.

---

## Features

### 🛒 E-commerce & Cart Operations
* **Dynamic Catalog**: Fetches products, ratings, and categories dynamically from the FakeStore API.
* **Product Detail**: Large details page view, review rating badge, and category filters.
* **Search & Filters**: Search catalog by title keywords, filter by categories, and sort by Price (ASC/DESC) or Title name (A-Z).
* **Cookie-Based Cart**: Maintains cart state (`{"items": {"prod_id": qty}}`) inside browser cookies (requires no backend database).
* **Quantity Updates**: Dynamically increment, decrement, or remove items from the cart.

### 🔐 Authentication & Accounts
* **Account Registration**: Client validation of username, email formatting, and passwords stored in the temporary session registry (`session["users"]`).
* **Secure Login / Logout**: Authenticates email/password combinations and manages user context (`session["user"]`).
* **Route Guards**: Restricts access to the Checkout and Account routes for guest users.
* **Password Reset**: Update credentials dynamically for registered session accounts.
* **Order History**: Captures shipping addresses, contact details, product list, and paid sums in `session["orders"]`.

### ⚡ Developer & Admin Integrations
* **Telegram Notifications**: Automatically formats and sends shipping summaries, item lists, and totals to an admin Telegram group upon checkout completion.
* **Local In-Memory TTL Cache**: Cache store results for 5 minutes, mitigating FakeStore API rate limits and boosting client load times.
* **Dismissible Alert Banners**: Context-specific alerts for success, warnings, and errors.
* **Custom Error Boundary**: Fully styled, user-friendly 404 Page Not Found and 500 Server Connection Error fallback templates.

---

## Folder Structure

```text
flaskProject/
│
├── app.py                      # Main Flask application entrypoint
├── requirements.txt            # Package dependencies
├── README.md                   # Installation & deployment documentation
├── .env.example                # Sample environment configurations
├── Procfile                    # WSGI process manager command for production
├── runtime.txt                 # Python platform version lock
├── .gitignore                  # Git untracked directories
│
├── services/
│   ├── product_service.py      # FakeStore API client with local TTL cache
│   └── telegram_service.py     # Telegram Bot API message dispatcher
│
├── utils/
│   ├── auth.py                 # Route-guard decorator (login_required)
│   ├── cart.py                 # Cookie cart operations & totals computations
│   └── helpers.py              # Email format regex & badge count validators
│
├── static/
│   ├── css/
│   │   └── styles.css          # Core custom styles (indigo/violet, glassmorphic UI)
│   ├── js/
│   └── images/
│
└── templates/
    ├── components/
    │   ├── navbar.html         # Header navigation, dynamic session tabs & cart badge
    │   ├── footer.html         # Grid columns, company links & support details
    │   ├── flash.html          # Custom alert box container
    │   └── product_card.html   # Reusable product grid display component
    │
    ├── base.html               # Parent HTML5 skeleton structure
    ├── home.html               # Hero intro banner, category list & product showcases
    ├── products.html           # Catalog page with search, filters & sort drop-downs
    ├── product_detail.html     # Multi-column description, numeric qty form & recommendations
    ├── cart.html               # Shopping cart table & summary breakdown
    ├── checkout.html           # Shipping address inputs & checkout values
    ├── checkout_success.html   # Order success invoice screen
    ├── login.html              # Sign in authentication form
    ├── register.html           # Account registration fields
    ├── reset_password.html     # Credentials update inputs
    ├── contact.html            # Helpdesk messaging form
    ├── account.html            # User dashboard showing profile details & order history
    ├── 404.html                # Not Found error boundary page
    └── 500.html                # Server Connection error page
```

---

## Installation & Setup

### 1. Clone & Initialize the Project
Extract or clone the repository to your local directory:
```bash
cd flaskProject
```

### 2. Configure Virtual Environment
Create and activate a virtual environment:
```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Package Dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` file to create your local `.env` configuration:
```bash
cp .env.example .env
```
Open `.env` and fill in your custom keys:
```env
FLASK_SECRET_KEY=your_secure_random_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_target_group_chat_id
```

---

## Running Locally

To start the built-in Flask development server:
```bash
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000/
```

---

## Deployment Playbook

### ☁️ Option 1: Render.com
1. Create a free account on [Render](https://render.com).
2. Connect your GitHub repository.
3. Create a new **Web Service**.
4. Configure settings:
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `gunicorn app:app`
5. Go to the **Environment** tab and add variables:
   * `FLASK_SECRET_KEY` = your secret key
   * `TELEGRAM_BOT_TOKEN` = your bot token
   * `TELEGRAM_CHAT_ID` = your group chat ID
6. Click **Deploy Web Service**.

### ☁️ Option 2: Railway.app
1. Create a free account on [Railway](https://railway.app).
2. Create a **New Project** and connect your GitHub repository.
3. Railway automatically detects the Python project through the `Procfile`.
4. Go to **Variables** and input your environment secrets (`FLASK_SECRET_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`).
5. Deployment will start and build automatically.

### ☁️ Option 3: PythonAnywhere
1. Create an account on [PythonAnywhere](https://www.pythonanywhere.com).
2. Open a bash console, clone your repository, and create a virtualenv:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 velocities-venv
   pip install -r requirements.txt
   ```
3. Go to the **Web** tab, create a new web app, and point it to your project path.
4. Set the path to the Virtualenv directory.
5. Edit your WSGI file (e.g., `/var/www/username_pythonanywhere_com_wsgi.py`) to import the Flask app:
   ```python
   import sys
   path = '/home/username/flaskProject'
   if path not in sys.path:
       sys.path.append(path)
   from app import app as application
   ```
6. Set env variables using your environment editor dashboard. Reload the web service.

---

## Screenshots Section
*(Add screenshots of your working e-commerce pages here after deployment)*
* **Homepage & Hero Banner**
* **Products Catalog Grid & Sidebar Filters**
* **Cart Page & Quantity Control**
* **Checkout Order Invoice**
* **User Account Dashboard & Past Orders**

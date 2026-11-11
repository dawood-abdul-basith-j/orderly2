# Orderly - Smart Food Ordering System

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-darkgreen.svg)](https://www.djangoproject.com/)
[![AI Assistant](https://img.shields.io/badge/Google%20Gemini-3.8%20Flash-orange.svg)](https://aistudio.google.com/)
[![CI](https://github.com/dawood-abdul-basith-j/orderly2/actions/workflows/python-app.yml/badge.svg)](https://github.com/dawood-abdul-basith-j/orderly2/actions/workflows/python-app.yml)

**Orderly** is a full-featured, AI-powered food ordering and kitchen management web application built with Django. It features an interactive food catalog, customizable item options, group ordering with shared carts, live order lifecycle tracking, staff kitchen panels, business analytics, and an integrated conversational AI chatbot powered by Google Gemini.

---

## Key Features

### 1. User Authentication & Profile
- **Flexible Sign-Up & Login**: Register with username, email, and mobile number. Users can log in using either their **username** or their **mobile number**.
- **User Profiles**: Manage delivery addresses, phone numbers, and dietary preferences (e.g., vegan, gluten-free, nut allergies).
- **Secure OTP Password Reset**: Request a 6-digit OTP sent to your verified email with expiration timers and automated fallbacks for offline/development environments.

### 2. Menu & Customization
- **Categorized Menu**: Browse items by category with real-time text search.
- **Dietary & Tag Filters**: Quick-filter by tags (e.g., vegetarian, spicy, gluten-free).
- **Customizable Options**: Multi-option groups for menu items (e.g., portion sizes, extra toppings, spice levels) with live price calculation.
- **Estimated Prep Times**: Preparation time tracking for each item to compute accurate delivery estimates.

### 3. Orders & Group Cart Sharing
- **Real-Time Cart**: Add, customize, and remove items with instant subtotal and tax calculation.
- **Group Ordering (Shared Cart)**: Host generates a unique 8-character share code or link allowing multiple people to contribute to a single group order.
- **Order Lifecycle Tracking**: Live statuses for customers: `Pending` &rarr; `Preparing` &rarr; `Cooking` &rarr; `Ready` &rarr; `Out for delivery` &rarr; `Delivered`.
- **Kitchen / Staff Panel**: Dedicated interface for restaurant staff to update cooking and delivery statuses in real-time.

### 4. AI Chatbot & Smart Recommendations
- **Google Gemini Integration**: Conversational assistant powered by `models/gemini-3.8-flash`.
- **Cart Automation via Chat**: Add items, delete items, inspect cart contents, and ask for menu recommendations using natural language.
- **Zero-Downtime Fallback**: Integrated rule-based parser ensures the chatbot continues working even if the external AI service or internet is unreachable.
- **Smart Recommendations**: Suggests popular dishes and personalized items based on user order history and dietary preferences.

### 5. Staff Analytics & Reviews
- **Analytics Dashboard**: Real-time sales metrics, order counts, top-selling items, recent orders, and average customer ratings for staff members.
- **Ratings & Reviews**: Verified customers can rate their delivered orders (1-5 stars) with comments.

---

## Tech Stack

- **Backend**: Python 3.10+, Django 5.x
- **Database**: MySQL (with automatic zero-config SQLite fallback for local development and CI)
- **AI / LLM**: Google Gemini API (`google-generativeai`)
- **Frontend**: Django Templates, HTML5, CSS3, JavaScript, FontAwesome
- **Testing & Quality**: Pytest, Pytest-Django, Flake8, GitHub Actions CI/CD

---

## Directory Structure

```text
├── analytics/              # Sales, top items, and rating dashboard for staff
├── chatbot/                # Conversational AI bot, Gemini client, & rule-based parser
├── menu/                   # Food catalog, categories, option groups, and tags
├── orders/                 # Cart, checkout, group shared orders, and kitchen panel
├── payments/               # Payment simulation (Cash on Delivery & Online)
├── reviews/                # Customer rating and review system
├── smart_features/         # Recommendation engine & dynamic query filters
├── smart_food/             # Project settings, URL routing, and WSGI configuration
├── static/                 # Global stylesheet and static frontend assets
├── templates/              # Base layout and shared application templates
├── users/                  # User accounts, authentication, OTP reset, and profiles
├── .env                    # Environment variables (API keys, DB config, SMTP)
├── .github/workflows/      # GitHub Actions CI workflow (flake8, pytest)
├── manage.py               # Django management script
├── pytest.ini              # Pytest configuration
└── requirements.txt        # Project dependencies
```

---

## Getting Started

### Prerequisites

- **Python**: Version 3.10 to 3.13 installed
- **Git**: Installed on your system
- **MySQL** *(Optional)*: MySQL Server 8.0+ running on port 3306 (if not running, the application automatically uses SQLite)

---

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd correction
   ```

2. **Create and activate a virtual environment**:
   - On Windows:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root (or update the existing one):
   ```ini
   # Google Gemini API
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=models/gemini-3.8-flash

   # Email / SMTP Configuration
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password_here
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

   # Database Configuration (Optional: defaults to MySQL with SQLite fallback)
   DB_ENGINE=mysql
   DB_NAME=smart_food_db
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=3306

   # Set to true to force SQLite during local testing:
   USE_SQLITE=false
   ```

5. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create an admin/staff account**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. Open your browser and navigate to:
   - **Customer Portal / Menu**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
   - **Staff Order Panel**: [http://127.0.0.1:8000/orders/employee-panel/](http://127.0.0.1:8000/orders/employee-panel/)
   - **Analytics Dashboard**: [http://127.0.0.1:8000/analytics/dashboard/](http://127.0.0.1:8000/analytics/dashboard/)

---

## Running Tests & Quality Checks

Run the complete automated test suite using **pytest**:
```bash
pytest -v
```

Or using Django's built-in test runner:
```bash
python manage.py test
```

Run code quality / linting checks:
```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

Run Django system configuration check:
```bash
python manage.py check
```

---

## Environment Variables Reference

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key from Google AI Studio | None |
| `GEMINI_MODEL` | Gemini model name | `models/gemini-3.8-flash` |
| `EMAIL_BACKEND` | Django email backend (`smtp` or `console`) | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST_USER` | SMTP username / sender address | None |
| `EMAIL_HOST_PASSWORD` | SMTP password / Gmail app password | None |
| `USE_SQLITE` | Force SQLite engine instead of MySQL | `false` |
| `DB_NAME` | MySQL database name | `smart_food_db` |
| `DB_USER` | MySQL database user | `root` |
| `DB_PASSWORD` | MySQL database password | `mYSQL908#2310` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `3306` |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames | `*` (in debug mode) |

---

## Troubleshooting

- **MySQL Server Offline**:
  If MySQL is not running on your machine, Orderly automatically switches to `db.sqlite3` without throwing connection errors. To explicitly use SQLite at any time, set `USE_SQLITE=true` in `.env`.
- **Email / Password Reset OTP Behind Strict Firewalls**:
  When testing locally or on campus/office networks with SSL inspection, Orderly automatically uses fallback TLS verification. In development mode (`DEBUG=True`), the generated OTP is also displayed in a friendly notification banner so you are never blocked.
- **Gemini Model 404 / Quota Issues**:
  Google deprecated earlier model versions for new users. Ensure `GEMINI_MODEL=models/gemini-3.8-flash` is set in `.env` for free-tier access and optimal performance.

---

## License

This project is developed for academic and educational purposes.


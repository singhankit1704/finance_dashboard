# Finance Dashboard Backend

A backend API for a finance dashboard system with role-based access control, financial record management, and summary analytics.

**Stack:** Python · Django · Django REST Framework · SQLite · JWT Authentication

---

## Table of Contents

- [Setup](#setup)
- [Seeding Data](#seeding-data)
- [Roles & Permissions](#roles--permissions)
- [API Reference](#api-reference)
- [Design Decisions & Assumptions](#design-decisions--assumptions)

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd finance_dashboard

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Apply migrations

```bash
python manage.py migrate
```

### 3. Seed sample data (optional)

```bash
python seed_data.py
```

This creates 3 ready-to-use accounts and 180 sample transactions:

| Username | Password    | Role     |
|----------|-------------|----------|
| admin    | Admin@123   | admin    |
| analyst  | Analyst@123 | analyst  |
| viewer   | Viewer@123  | viewer   |

### 4. Run the server

```bash
python manage.py runserver
```

API is available at: `http://127.0.0.1:8000/`

---

## Roles & Permissions

| Action                             | Viewer | Analyst | Admin |
|------------------------------------|--------|---------|-------|
| Login                              | ✅     | ✅      | ✅    |
| View own profile (`/me`)           | ✅     | ✅      | ✅    |
| List/create/update/delete users    | ❌     | ❌      | ✅    |
| View transactions (own)            | ✅     | ✅      | ✅    |
| View transactions (all users)      | ❌     | ❌      | ✅    |
| Create/update/delete transactions  | ❌     | ❌      | ✅    |
| Dashboard summary                  | ✅     | ✅      | ✅    |
| Category breakdown & trends        | ❌     | ✅      | ✅    |
| Recent activity                    | ✅     | ✅      | ✅    |

---

## API Reference

All protected endpoints require the header:
```
Authorization: Bearer <access_token>
```

---

### Authentication

#### `POST /api/auth/login/`
Login with username and password.

**Request:**
```json
{ "username": "admin", "password": "Admin@123" }
```

**Response `200`:**
```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "access": "<jwt_access_token>",
    "refresh": "<jwt_refresh_token>",
    "user": { "id": 1, "username": "admin", "role": "admin", ... }
  }
}
```

#### `POST /api/auth/refresh/`
Get a new access token using a refresh token.

**Request:**
```json
{ "refresh": "<refresh_token>" }
```

---

### Users  *(Admin only)*

#### `GET /api/users/`
List all users. Optional filters: `?role=viewer|analyst|admin`, `?is_active=true|false`

#### `POST /api/users/`
Create a new user.
```json
{
  "username": "john",
  "password": "John@1234",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "analyst"
}
```

#### `GET /api/users/me/`  *(All roles)*
Returns the currently authenticated user's profile.

#### `GET /api/users/<id>/`
Get a specific user.

#### `PATCH /api/users/<id>/`
Update a user's role, status, or name.
```json
{ "role": "analyst", "is_active": true }
```

#### `DELETE /api/users/<id>/`
Soft-deactivates the user (sets `is_active=false`). Does not hard-delete.

---

### Transactions

#### `GET /api/transactions/`  *(All roles)*
List transactions. Admins see all; viewers/analysts see only their own.

**Filters:**
| Param        | Description                        | Example                  |
|--------------|------------------------------------|--------------------------|
| `type`       | `income` or `expense`              | `?type=income`           |
| `category`   | Category name                      | `?category=salary`       |
| `date_from`  | Start date (`YYYY-MM-DD`)          | `?date_from=2026-01-01`  |
| `date_to`    | End date (`YYYY-MM-DD`)            | `?date_to=2026-03-31`    |
| `amount_min` | Minimum amount                     | `?amount_min=1000`       |
| `amount_max` | Maximum amount                     | `?amount_max=5000`       |
| `search`     | Search in description or category  | `?search=salary`         |
| `ordering`   | `amount`, `-amount`, `date`, `-date` | `?ordering=-date`      |
| `page`       | Pagination                         | `?page=2`                |

#### `POST /api/transactions/`  *(Admin only)*
Create a new transaction.
```json
{
  "amount": 5000.00,
  "type": "income",
  "category": "salary",
  "date": "2026-04-01",
  "description": "April salary"
}
```

**Available categories:**
`salary`, `freelance`, `investment`, `rent`, `food`, `transport`, `utilities`, `healthcare`, `entertainment`, `education`, `other`

#### `GET /api/transactions/<id>/`
Get a single transaction.

#### `PATCH /api/transactions/<id>/`  *(Admin only)*
Update a transaction.

#### `DELETE /api/transactions/<id>/`  *(Admin only)*
Soft-delete a transaction (`is_deleted=true`). Deleted records are excluded from all queries and dashboard calculations.

---

### Dashboard

#### `GET /api/dashboard/summary/`  *(All roles)*
Returns global totals (admin) or personal totals (others).
```json
{
  "total_income": 409656.85,
  "total_expenses": 132972.51,
  "net_balance": 276684.34
}
```

#### `GET /api/dashboard/categories/`  *(Analyst, Admin)*
Category-wise income and expense totals.
```json
{
  "salary":     { "income": 153657.33, "expense": 0.0,    "count": 29 },
  "food":       { "income": 0.0,       "expense": 15400.0, "count": 12 }
}
```

#### `GET /api/dashboard/trends/monthly/`  *(Analyst, Admin)*
Monthly income vs expense (all time).
```json
{
  "2026-01": { "income": 45000.0, "expense": 12000.0 },
  "2026-02": { "income": 38000.0, "expense": 9500.0 }
}
```

#### `GET /api/dashboard/trends/weekly/`  *(Analyst, Admin)*
Weekly income vs expense for the last 8 weeks.

#### `GET /api/dashboard/recent/`  *(All roles)*
Returns the 10 most recent transactions.

---

## Error Response Format

All errors follow a consistent structure:
```json
{
  "success": false,
  "message": "Human-readable description of the error.",
  "errors": { ... }
}
```

| Status | Meaning                          |
|--------|----------------------------------|
| 400    | Validation error / bad input     |
| 401    | Missing or invalid token         |
| 403    | Insufficient role permissions    |
| 404    | Resource not found               |

---

## Project Structure

```
finance_dashboard/
├── finance_dashboard/
│   ├── settings.py          # App config, DRF, JWT settings
│   └── urls.py              # Root URL routing
├── users/
│   ├── models.py            # Custom User model with roles
│   ├── serializers.py       # User serializers (read/create/update)
│   ├── views.py             # Auth, User CRUD views
│   ├── permissions.py       # IsAdmin, IsAnalystOrAdmin, IsAnyRole
│   ├── exceptions.py        # Global error response formatter
│   └── urls.py
├── transactions/
│   ├── models.py            # Transaction model with soft delete
│   ├── serializers.py       # Transaction serializers
│   ├── filters.py           # django-filter FilterSet
│   ├── views.py             # Transaction CRUD views
│   ├── dashboard_views.py   # Summary, categories, trends, recent
│   ├── urls.py
│   └── dashboard_urls.py
├── seed_data.py             # Seeds 3 users + 180 transactions
├── requirements.txt
└── README.md
```

---

## Design Decisions & Assumptions

**Role hierarchy:** Admin ⊃ Analyst ⊃ Viewer. An admin inherits all analyst and viewer access. This is encoded in `is_analyst` and `is_viewer` properties on the User model rather than a permission matrix, keeping it simple and readable.

**Data visibility:** Viewers and analysts can only see their own transactions. This is a common multi-tenant pattern — it ensures data isolation without requiring a separate tenant model. Admins have full visibility.

**Soft delete:** Both users (deactivation) and transactions (`is_deleted=True`) use soft deletes. This preserves historical data and audit trails, which is critical in finance systems. Hard deletes are never performed.

**JWT authentication:** Tokens expire in 24 hours; refresh tokens in 7 days with rotation enabled. This is a reasonable default for a dashboard app that runs in a browser.

**SQLite:** Chosen for zero-setup local development. The ORM layer (Django/SQLAlchemy) means switching to PostgreSQL in production requires only a one-line settings change.

**Pagination:** All list endpoints paginate at 20 records per page by default.

**Assumption — who creates transactions:** Only admins can create/edit/delete transactions. In a real system, this might be extended so analysts can also create records. This was a conservative default given the assignment's wording.

**Assumption — category list is fixed:** Categories are an enumerated field rather than a free-text or foreign key. This ensures consistency in dashboard grouping and avoids duplicates like "Food" vs "food" vs "Food & Dining".

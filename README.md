# CrowdLabel System

Crowdsourcing Image Annotation System

## Project Overview

CrowdLabel is a crowdsourcing-based image annotation system that supports multi-user collaborative labeling, automatic consensus detection, manual review, and payment management. The system uses a frontend-backend separation architecture with Django REST Framework as the backend API and React + TypeScript as the frontend framework.


## Project Structure

```
crowdlabel_system/
├── frontend/                    # React + Vite + TypeScript Frontend
│   ├── src/
│   │   ├── services/
│   │   │   └── api.ts          # API service
│   │   ├── types.ts            # TypeScript types
│   │   ├── main.tsx            # React entry
│   │   └── index.css           # Global styles
│   ├── APP.tsx                 # Main app component
│   ├── index.html              # HTML entry
│   ├── package.json            # Frontend dependencies
│   ├── vite.config.ts          # Vite config
│   ├── tsconfig.json           # TypeScript config
│   └── tailwind.config.js      # TailwindCSS config
│
├── backend/                     # Django REST Framework Backend
│   ├── api/                    # API application
│   │   ├── models.py           # Database models
│   │   ├── views.py            # API views
│   │   ├── serializers.py      # Serializers
│   │   ├── urls.py             # URL routes
│   │   └── migrations/         # Database migrations
│   ├── crowdlabel_backend/     # Django project config
│   │   ├── settings.py         # Settings
│   │   ├── urls.py             # Root URL config
│   │   └── wsgi.py             # WSGI config
│   ├── scripts/                # Utility scripts
│   │   ├── generate_test_data.py  # Test data generator
│   │   ├── test_queries.py        # Query test
│   │   └── export_schema.sql      # Database schema
│   ├── manage.py               # Django management
│   └── requirements.txt        # Python dependencies
│
├── .gitignore                  # Git ignore file
└── README.md                   # This file
```

## Requirements

### Backend
- Python 3.11+
- MySQL 8.0+
- Django 5.0+
- Django REST Framework

### Frontend
- Node.js 18+
- npm or yarn

## Quick Start

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd crowdlabel_system
```

### 2. Database Setup

**Start MySQL service:**
- Windows: `net start MySQL` (admin required)
- Linux/Mac: `sudo systemctl start mysql`

**Create database:**
```sql
mysql -u root -p
CREATE DATABASE crowdlabel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

**Update config:**
Edit `backend/crowdlabel_backend/settings.py`:
```python
'PASSWORD': 'your_password',  # your MySQL password
```

### 3. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Generate test data (optional)
python scripts/generate_test_data.py

# Start server
python manage.py runserver
```

Backend runs at `http://localhost:8000`

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at `http://localhost:5173`

## Database Schema

### Tables

1. **api_user** - User table
   - Fields: `id`, `username`, `role`, `status`, `balance_wallet`
   - Indexes: `username` (UNIQUE)

2. **api_image** - Image task table
   - Fields: `id`, `image_url`, `category_options`, `final_label`, `review_status`, `bounty`, `assigned_count`, `status`, `created_at`
   - Indexes: `(status, assigned_count)`

3. **api_annotation** - Annotation table
   - Fields: `id`, `user_id`, `image_id`, `submitted_label`, `is_correct`, `payment_id`, `created_at`
   - Unique: `(user_id, image_id)` - prevent duplicate

4. **api_payment** - Payment table
   - Fields: `id`, `annotator_id`, `amount`, `payment_date`

### Schema File

Full schema: `backend/scripts/export_schema.sql`

### Test Data

```bash
cd backend
python scripts/generate_test_data.py
```

Creates:
- Admin: `admin` / `admin123`
- Annotators: `annotator1-10` / `123`
- 1000 image tasks with sample annotations

## API Endpoints

### Auth
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/check/` - Check auth status

### Annotator
- `GET /api/tasks/next/` - Get next task
- `POST /api/annotate/` - Submit annotation
- `GET /api/stats/` - Get user stats
- `GET /api/history/` - Get annotation history

### Admin
- `GET /api/admin/reviews/` - Get review queue
- `POST /api/admin/resolve/` - Resolve conflict
- `GET /api/admin/unpaid/` - Get unpaid users
- `POST /api/admin/payroll/` - Process payments
- `GET /api/tasks/active/` - Get active tasks
- `POST /api/tasks/add/` - Add new task

## Tech Stack

### Frontend
- React 18, TypeScript, Vite, TailwindCSS, Recharts

### Backend
- Django 5.0+, Django REST Framework, MySQL

## Core Features

1. **User Management** - Admin and Annotator roles
2. **Task Distribution** - Auto-assign tasks (prioritize near-completion)
3. **Consensus Mechanism** - 5/5 unanimous = auto-approve, else manual review
4. **Payment System** - Batch payment processing
5. **Statistics** - Accuracy rate, pending balance, history

## Notes

1. Make sure MySQL is running
2. Create database before first run
3. Use `scripts/generate_test_data.py` for demo data

## Documentation

- **Database Schema:** [backend/scripts/export_schema.sql](backend/scripts/export_schema.sql)

## License

Course project for CityuDS5003.

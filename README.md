# Software Access Key Management System

A Flask-based web application for managing educational API keys with SQLAlchemy, Alembic, and a beautiful frontend.

## Features

- User registration and authentication (Session-based)
- Beautiful web interface with modern design
- API key generation with expiration dates
- API key revocation
- API key validation
- PostgreSQL database with Alembic migrations
- REST API endpoints (Basic Auth)

## Tech Stack

- Flask 3.1.3
- SQLAlchemy 2.1.6
- Alembic 1.20.1
- PostgreSQL 16
- Pydantic 2.10.4
- Docker & Docker Compose
- HTML5 & CSS3 (Custom modern design)

## Project Structure

```
.
├── src/
│   ├── database.py    # Database models and session management
│   ├── routes.py      # REST API endpoints & Web routes
│   ├── schemas.py     # Pydantic schemas for validation
│   ├── service.py     # Business logic layer
│   └── utils.py       # Utility functions (key generation, hashing)
├── templates/         # HTML templates for web interface
│   ├── base.html      # Base template with navigation
│   ├── register.html  # Registration page
│   ├── login.html     # Login page
│   ├── dashboard.html # API keys dashboard
│   ├── create_key.html # Create new API key
│   └── validate.html  # Validate API key
├── static/
│   └── css/
│       └── style.css  # Custom CSS styling
├── alembic/           # Database migrations
├── main.py            # Application entry point
├── docker-compose.yml # Docker services configuration
├── Dockerfile         # Container image definition
└── requirements.txt   # Python dependencies
```

## Setup with Docker Compose (Colima)

1. Start the services:
```bash
docker-compose up -d
```

2. Wait for PostgreSQL to be ready, then initialize the database:
```bash
docker-compose exec web alembic upgrade head
```

3. The web interface will be available at `http://localhost:5001`

## Web Interface

The application includes a beautiful web interface accessible at `http://localhost:5001`

### Web Pages

1. **/** - Redirects to login or dashboard based on auth status
2. **/api/register** - Registration page (GET/POST)
3. **/api/login** - Login page (GET/POST)
4. **/api/dashboard** - Dashboard with list of API keys (requires login)
5. **/api/create-key** - Create new API key page (requires login)
6. **/api/validate** - Validate API key page (public)
7. **/api/logout** - Logout

### Features

- Modern gradient design with glassmorphism effects
- Responsive layout for mobile devices
- Flash messages for user feedback
- One-click key copying
- Visual status badges for keys
- Auto-hiding notifications

## API Endpoints

### Authentication

API endpoints (JSON) use Basic Authentication. Web interface uses session-based authentication.

### 1. Register User
**POST** `/api/users/register`

Request body:
```json
{
  "username": "testuser",
  "password": "securepassword"
}
```

Response:
```json
{
  "id": 1,
  "username": "testuser",
  "created_at": "2026-11-01T10:00:00",
  "is_active": true
}
```

### 2. Create API Key
**POST** `/api/api-keys` (requires authentication)

Request body:
```json
{
  "name": "My Test Key",
  "description": "Key for testing purposes",
  "expires_in_days": 30
}
```

Response:
```json
{
  "id": 1,
  "key_value": "ak_abc123...",
  "name": "My Test Key",
  "description": "Key for testing purposes",
  "created_at": "2026-11-01T10:00:00",
  "expires_at": "2026-12-01T10:00:00",
  "is_active": true,
  "is_revoked": false
}
```

### 3. List API Keys
**GET** `/api/api-keys` (requires authentication)

Response:
```json
[
  {
    "id": 1,
    "key_value": "ak_abc123...",
    "name": "My Test Key",
    "description": "Key for testing purposes",
    "created_at": "2026-11-01T10:00:00",
    "expires_at": "2026-12-01T10:00:00",
    "is_active": true,
    "is_revoked": false
  }
]
```

### 4. Revoke API Key
**POST** `/api/api-keys/{key_id}/revoke` (requires authentication)

Response:
```json
{
  "id": 1,
  "key_value": "ak_abc123...",
  "name": "My Test Key",
  "description": "Key for testing purposes",
  "created_at": "2026-11-01T10:00:00",
  "expires_at": "2026-12-01T10:00:00",
  "is_active": false,
  "is_revoked": true
}
```

### 5. Validate API Key
**POST** `/api/api-keys/validate` (no authentication required)

Request body:
```json
{
  "key_value": "ak_abc123..."
}
```

Response:
```json
{
  "is_valid": true,
  "is_active": true,
  "is_expired": false,
  "is_revoked": false,
  "key_id": 1,
  "key_name": "My Test Key",
  "owner_id": 1,
  "expires_at": "2026-12-01T10:00:00"
}
```

### 6. Health Check
**GET** `/api/health`

Response:
```json
{
  "status": "healthy"
}
```

## Example Usage

### Web Interface

1. Open `http://localhost:5000` in your browser
2. Click "Регистрация" to create an account
3. Login with your credentials
4. Create API keys from the dashboard
5. Validate keys using the "Проверить ключ" page

### API with cURL

```bash
# Register a user
curl -X POST http://localhost:5000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"securepassword"}'

# Create an API key (with Basic Auth)
curl -X POST http://localhost:5000/api/api-keys \
  -H "Content-Type: application/json" \
  -u testuser:securepassword \
  -d '{"name":"Test Key","description":"Test","expires_in_days":30}'

# List API keys
curl -X GET http://localhost:5000/api/api-keys \
  -u testuser:securepassword

# Validate an API key
curl -X POST http://localhost:5000/api/api-keys/validate \
  -H "Content-Type: application/json" \
  -d '{"key_value":"ak_abc123..."}'

# Revoke an API key
curl -X POST http://localhost:5000/api/api-keys/1/revoke \
  -u testuser:securepassword
```

## Database Migrations

To create a new migration:
```bash
docker-compose exec web alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:
```bash
docker-compose exec web alembic upgrade head
```

To rollback:
```bash
docker-compose exec web alembic downgrade -1
```

## Development

Run without Docker (requires PostgreSQL running locally):
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/access_keys"
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python main.py
```

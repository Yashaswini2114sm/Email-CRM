# 📧 Email CRM API

A full-featured **Customer Relationship Management** backend built with **FastAPI**, featuring AI-powered ticket analysis, real-time WebSocket notifications, background job processing, and email integration.

> **Purpose**: This project is designed as a learning resource for backend development with Python. Every file is heavily commented to explain _why_ things are done, not just _what_ they do.

---

## 🏗️ Architecture Overview

```
email-crm/
├── src/                        # All application source code
│   ├── main.py                 # FastAPI app entry point
│   ├── api/                    # HTTP route handlers (controllers)
│   │   ├── auth.py             # Register, login, profile endpoints
│   │   ├── tickets.py          # CRUD + messaging for support tickets
│   │   ├── emails.py           # IMAP fetch + SMTP send
│   │   ├── ai.py               # AI intent detection + reply generation
│   │   └── documents.py        # File upload + listing
│   ├── core/                   # Cross-cutting concerns
│   │   ├── config.py           # Environment config via Pydantic Settings
│   │   ├── security.py         # Password hashing + JWT tokens
│   │   ├── dependencies.py     # FastAPI dependency injection (auth guards)
│   │   └── logger.py           # Centralized logging setup
│   ├── database/               # Database connection layer
│   │   ├── base.py             # SQLAlchemy declarative base
│   │   └── session.py          # Engine + session factory
│   ├── models/                 # SQLAlchemy ORM models (database tables)
│   │   ├── user.py             # Users table
│   │   ├── ticket.py           # Support tickets table
│   │   ├── message.py          # Conversation messages table
│   │   └── document.py         # File attachments table
│   ├── schemas/                # Pydantic models (request/response shapes)
│   │   ├── user.py             # User creation, login, response
│   │   ├── ticket.py           # Ticket CRUD schemas
│   │   ├── message.py          # Message schemas
│   │   └── document.py         # Document response schemas
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py     # User registration + authentication
│   │   ├── ticket_service.py   # Ticket CRUD operations
│   │   ├── email_service.py    # IMAP/SMTP email handling
│   │   ├── ai_service.py       # OpenAI integration
│   │   └── document_service.py # File storage + AI validation
│   ├── websockets/             # Real-time communication
│   │   └── notifications.py    # WebSocket connection manager
│   └── workers/                # Background job processors
│       ├── email_worker.py     # Async email processing via Dramatiq
│       └── ai_worker.py        # Async AI analysis via Dramatiq
├── tests/                      # Automated test suite
│   ├── conftest.py             # Shared fixtures (in-memory SQLite DB)
│   ├── test_auth.py            # Authentication tests
│   ├── test_tickets.py         # Ticket CRUD tests
│   ├── test_emails.py          # Email endpoint tests
│   ├── test_ai.py              # AI endpoint tests (mocked)
│   └── test_documents.py       # Document upload tests
├── alembic/                    # Database migrations
│   ├── env.py                  # Migration environment config
│   ├── script.py.mako          # Migration template
│   └── versions/               # Individual migration files
├── uploads/                    # Uploaded document storage
├── alembic.ini                 # Alembic configuration
├── docker-compose.yml          # PostgreSQL + Redis + API + Worker
├── Dockerfile                  # Container build instructions
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore                  # Git exclusions
└── .github/workflows/ci.yml   # GitHub Actions CI pipeline
```

---

## 🧩 Key Concepts (For Learning)

### Layered Architecture
The project follows a **3-layer architecture**:

1. **API Layer** (`src/api/`) — Handles HTTP requests, validates input, returns responses. Never contains business logic.
2. **Service Layer** (`src/services/`) — Contains all business logic. Reusable across API routes and background workers.
3. **Data Layer** (`src/models/`, `src/database/`) — Defines database tables and manages connections.

### Why This Matters
- **Separation of concerns**: Each layer has one job. If you need to change how passwords are hashed, you only touch `security.py`.
- **Testability**: You can test services without HTTP, and test API routes with a mock database.
- **Reusability**: The `create_ticket()` service is used by both the API route AND the email worker.

### Dependency Injection
FastAPI's `Depends()` system injects database sessions and authenticated users into route handlers. See `src/core/dependencies.py` for the pattern.

### Background Jobs
Heavy operations (email fetching, AI analysis) are offloaded to **Dramatiq workers** that process jobs from a Redis queue. This keeps the API responsive.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose (for PostgreSQL + Redis)

### 1. Clone & Setup
```bash
cd email-crm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your values (the defaults work for local Docker setup)
```

### 3. Start Infrastructure
```bash
# Start PostgreSQL and Redis
docker compose up db redis -d
```

### 4. Run Database Migrations
```bash
alembic upgrade head
```

### 5. Start the API Server
```bash
uvicorn src.main:app --reload --port 8000
```

### 6. Open API Documentation
Visit **http://localhost:8000/docs** for the interactive Swagger UI.

---

## 🎨 React Frontend Dashboard

This project includes a clean, professional React frontend built with Vite, React Router, and vanilla CSS to interact with the backend API. 

### Starting the Frontend
Open a new terminal window/tab:
```bash
cd frontend
npm install
npm run dev
```
Visit **http://localhost:5173** in your browser.

### Workflow & Functionality

1. **Authentication**
   - **Register**: Go to the `/register` page and create a new agent account.
   - **Login**: Go to the `/login` page with your credentials. 
   - *How it works*: On login, the backend returns a JWT (JSON Web Token). The frontend stores this in `localStorage` and automatically attaches it to the `Authorization: Bearer <token>` header for all subsequent API requests.

2. **Dashboard (Ticket List)**
   - Once logged in, you land on the Dashboard (`/`).
   - *How it works*: It fetches all tickets via `GET /api/v1/tickets/`. You can use the dropdown to filter tickets by status (Open, In Progress, Resolved, Closed).

3. **Ticket Detail & Conversation**
   - Click any ticket to view its details (`/tickets/:id`).
   - *How it works*: The page concurrently fetches the ticket details, the message thread, and attached documents.
   - **Replying**: Type a message in the input box and hit "Send Reply". This hits `POST /api/v1/tickets/{id}/messages`.

4. **AI Reply Generation**
   - Inside a ticket, click **"✨ Suggest AI Reply"**.
   - *How it works*: It sends a request to `POST /api/v1/ai/generate-reply`. The backend uses OpenAI to read the ticket context and generate an appropriate, professional response which is added directly to the thread.

5. **Document Uploads**
   - On the right sidebar of a ticket, click **"Upload File"**.
   - *How it works*: You can upload files up to 10MB (PDF, Images, Word docs). The frontend sends this as `multipart/form-data` to `POST /api/v1/tickets/{id}/documents`. The backend validates the type, saves the file, and returns the document metadata.

---

## 🐳 Docker (Full Stack)

Run everything in containers:
```bash
docker compose up --build
```

This starts:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **FastAPI API** on port 8000
- **Dramatiq Worker** for background jobs

---

## 🧪 Running Tests

Tests use an **in-memory SQLite database** — no PostgreSQL needed.

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ -v --tb=short
```

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Create new user | ❌ |
| POST | `/api/v1/auth/login` | Get JWT token | ❌ |
| GET | `/api/v1/auth/me` | Get current user profile | ✅ |

### Tickets
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/tickets/` | Create ticket | ✅ |
| GET | `/api/v1/tickets/` | List tickets (paginated) | ✅ |
| GET | `/api/v1/tickets/{id}` | Get single ticket | ✅ |
| PATCH | `/api/v1/tickets/{id}` | Update ticket | ✅ |
| GET | `/api/v1/tickets/{id}/messages` | Get conversation | ✅ |
| POST | `/api/v1/tickets/{id}/messages` | Send reply | ✅ |
| POST | `/api/v1/tickets/{id}/documents` | Upload document | ✅ |
| GET | `/api/v1/tickets/{id}/documents` | List documents | ✅ |

### Emails
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/emails/process` | Fetch & process inbox | 🔒 Admin |
| POST | `/api/v1/emails/send` | Send email | ✅ |

### AI
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/ai/analyze` | Detect customer intent | ✅ |
| POST | `/api/v1/ai/generate-reply` | AI-generated response | ✅ |
| POST | `/api/v1/ai/validate-documents` | Validate documents | ✅ |

### System
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | ❌ |
| WS | `/ws/notifications` | Real-time updates | ✅ (token in query) |

---

## 🔑 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...localhost:5432/email_crm` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `SECRET_KEY` | `change-this-...` | JWT signing secret (**change in production!**) |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token TTL |
| `OPENAI_API_KEY` | _(empty)_ | OpenAI API key for AI features |
| `MAIL_USERNAME` | _(empty)_ | Email account username |
| `MAIL_PASSWORD` | _(empty)_ | Email account app password |
| `MAIL_IMAP_SERVER` | `imap.gmail.com` | IMAP server address |
| `MAIL_SMTP_SERVER` | `smtp.gmail.com` | SMTP server address |

---

## 📚 Learning Path

If you're new to this project, read the files in this order:

1. **Config & Setup**: `config.py` → `session.py` → `base.py`
2. **Models**: `user.py` → `ticket.py` → `message.py` → `document.py`
3. **Schemas**: `schemas/user.py` → `schemas/ticket.py`
4. **Security**: `security.py` → `dependencies.py`
5. **Services**: `auth_service.py` → `ticket_service.py`
6. **API Routes**: `api/auth.py` → `api/tickets.py` → `api/emails.py`
7. **Advanced**: `ai_service.py` → `workers/` → `websockets/`
8. **DevOps**: `Dockerfile` → `docker-compose.yml` → `ci.yml`
9. **Tests**: `conftest.py` → `test_auth.py` → `test_tickets.py`

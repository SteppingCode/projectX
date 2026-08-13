# Bookmarks API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.139+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D.svg?style=flat&logo=redis)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat&logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB.svg?style=flat&logo=python)](https://www.python.org/)

A high-performance, asynchronous RESTful API for modern bookmark management. Built with Python, FastAPI, PostgreSQL, and Redis, **Bookmarks API** provides automated web metadata scraping, full-text search with relevance ranking, tag management, JWT authentication with token refresh pairs, and intelligent caching.

---

## 📐 Architecture & Key Features

* **Asynchronous Execution Model**: End-to-end non-blocking operations powered by `asyncio`, `FastAPI`, `asyncpg`, and `httpx`.
* **Robust JWT Authentication**: Dual-token architecture using `HS256` signed short-lived Access Tokens (15 min) and long-lived Refresh Tokens (7 days) with strict type claim validations.
* **Automated Web Scraping**: Asynchronous HTML metadata extraction (`title`, `description`, `OpenGraph`) upon saving new URLs using `httpx` and `BeautifulSoup4`.
* **PostgreSQL Full-Text Search**: Native Russian-language full-text search engine utilizing `tsvector` indexing, `websearch_to_tsquery` parsing, and weighted title/tag relevance ranking (`ts_rank`).
* **Intelligent Caching Layer**: Automated query response caching via Redis with dynamic cache invalidation on write/update/delete operations.
* **Containerized Deployment**: Ready-to-use Docker Compose setup with automated database schema migrations and health checks.

---

## 🛠️ Technology Stack

| Category | Technology |
| :--- | :--- |
| **Framework** | FastAPI, Starlette, Pydantic v2 |
| **Database** | PostgreSQL 16 (via `asyncpg`) |
| **Caching & Broker** | Redis 7 (via `redis.asyncio`) |
| **Security** | PyJWT, Passlib / Bcrypt |
| **Web Scraping** | HTTPX, BeautifulSoup4 |
| **Orchestration** | Docker, Docker Compose |

---

## 📂 Directory Structure

```text
 projectX/
 ├── database/
 │   ├── database.py     # Database connection lifecycle & raw asyncpg queries
 │   ├── models.py       # Pydantic models & request validation schemas
 │   └── schemas/        # SQL schema files loaded dynamically on startup
 ├── app.py              # Main application entry point, lifespan, & routing
 ├── auth.py             # JWT token generation, pass hashing & dependency injection
 ├── parser.py           # Asynchronous web scraper for link metadata extraction
 ├── docker-compose.yml  # Multi-container service definition
 ├── Dockerfile          # Production Docker build specification
 ├── requirements.txt    # Project dependencies
 └── .env.example        # Environment variable template
```

## ⚙️ Environment Variables

Create a .env file in the root directory based on .env.example:

```Code snippet
SECRET_KEY="your-super-secret-production-key"
POSTGRES_USER="my_db_user"
POSTGRES_PASSWORD="generate_strong_password_here"
POSTGRES_DB="bookmarks_db"
PG_LINK="postgresql://my_db_user:generate_strong_password_here@db:5432/bookmarks_db"
REDIS_URL="redis://redis:6379"
```

## 🚀 Getting Started

### Method 1: Running with Docker Compose (Recommended)

Clone the repository:

```Bash
git clone [https://github.com/SteppingCode/projectX.git](https://github.com/SteppingCode/projectX.git)
cd projectX
```

Configure environment:

```Bash
cp .env.example .env
```

Launch the stack:

```Bash
docker compose up --build -d
```

Verify application status:

**The API will be available at http://localhost:8000.** Interactive documentation is hosted at:

- **Swagger UI: http://localhost:8000/api/docs**

- **ReDoc: http://localhost:8000/api/redoc**

### Method 2: Local Development Setup

Prerequisites

- Python 3.14+

- PostgreSQL 16 server

- Redis server

Set up virtual environment:

```Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```Bash
pip install -r requirements.txt
```

Run the server:

```Bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

## 📡 API Reference Overview

### 🔐 Authentication (/api/auth)

| Method | Endpoint | Description | Auth Required |
| :----: | --- | --- | :----: |
| POST | /api/auth/register | Register a new user account | ❌ No |
| POST | /api/auth/login | Authenticate user & receive Access/Refresh token pair | ❌ No |
| POST | /api/auth/refresh | Exchange valid Refresh Token for new token pair | ❌ No |

### 🔖 Bookmarks Management (/api)

| Method |Endpoint | Description | Auth Required |
| :----: | --- | --- | :----: |
| GET | /api/bookmarks | Retrieve cached list of user bookmarks | 🔒 Bearer |
| POST | /api/add_bookmark/ | Add new bookmark (triggers async metadata scraping) | 🔒 Bearer |
| GET | /api/bookmarks/search | Full-text relevance search over bookmarks & tags | 🔒 Bearer |
| DELETE | /api/delete_bookmark/{id} | Remove bookmark by ID & invalidate cache | 🔒 Bearer |
| POST | /api/bookmarks/{id}/tags | Attach tag to bookmark | 🔒 Bearer |
| DELETE | /api/bookmarks/{id}/tags/{tag} | Remove tag from bookmark | 🔒 Bearer |

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

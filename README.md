# Cloud-Native Task Management API

A production-style REST API for managing personal tasks, built with FastAPI, PostgreSQL, Docker, GitHub Actions, Terraform, and Microsoft Azure.

## Current Functionality

- Application health endpoint
- Automated health endpoint test

## Tech Stack

- Python 3.13
- FastAPI
- Uvicorn
- Pytest
- PostgreSQL *(coming soon)*
- SQLAlchemy and Alembic *(coming soon)*
- Docker *(coming soon)*
- Terraform and Azure *(coming soon)*

## Project Structure

```text
.
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_health.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Local Development

### 1. Create a virtual environment

```bash
python3.13 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### 2. Install the project

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 3. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- API: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health
- Swagger documentation: http://127.0.0.1:8000/docs
- ReDoc documentation: http://127.0.0.1:8000/redoc

### 4. Run the tests

```bash
pytest -v
```

## API Endpoints

| Method | Endpoint | Description | Authentication |
| --- | --- | --- | --- |
| GET | `/health` | Check whether the API is online | No |

More endpoints will be added as the project develops.

## Planned Features

- User registration and login
- JWT authentication
- Task creation and management
- User-specific task authorization
- PostgreSQL persistence
- Database migrations with Alembic
- Automated API testing
- Docker and Docker Compose
- GitHub Actions CI/CD
- Azure deployment using Terraform
- HTTPS and application health checks

## License

This project is intended for learning and portfolio purposes.

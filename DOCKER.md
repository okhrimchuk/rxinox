# Docker Setup for Rxinox

This project is containerized using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your actual secrets and configuration values.

2. **Build and run the containers:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Open http://localhost:8000 in your browser

4. **Stop the containers:**
   ```bash
   docker-compose down
   ```

## Services

### Web Service
- Django application running on port 8000
- Automatically runs migrations and loads catalog data on first startup
- Static files are collected automatically

### Database Service
- PostgreSQL database (optional, falls back to SQLite if not configured)
- Data persisted in Docker volume

## Environment Variables

All environment variables are configured in the `.env` file. Copy `.env.example` to `.env` and fill in your values:

**Required Variables:**
- `SECRET_KEY`: Django secret key (generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- `DEBUG`: Set to `True` for development, `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

**Database Variables (when using PostgreSQL):**
- `DATABASE`: Set to `postgres` to use PostgreSQL, leave empty for SQLite
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `SQL_HOST`: Database host (default: `db` in Docker)
- `SQL_PORT`: Database port (default: `5432`)

**Email Variables (optional, for future order email functionality):**
- `EMAIL_BACKEND`: Email backend to use
- `EMAIL_HOST`: SMTP server host
- `EMAIL_PORT`: SMTP server port
- `EMAIL_USE_TLS`: Use TLS (True/False)
- `EMAIL_HOST_USER`: Email account username
- `EMAIL_HOST_PASSWORD`: Email account password
- `MANAGER_EMAIL`: Manager email address for order notifications

## Volumes

- `postgres_data`: PostgreSQL database data
- `static_volume`: Collected static files
- `media_volume`: User uploaded media files

## Development

For development with hot-reload, the code is mounted as a volume. Changes to Python files will require a container restart:

```bash
docker-compose restart web
```

## Production Considerations

Before deploying to production:

1. Change `SECRET_KEY` to a secure random string
2. Set `DEBUG=0`
3. Configure proper `ALLOWED_HOSTS`
4. Set up proper database credentials
5. Use a production web server (e.g., Gunicorn + Nginx)
6. Configure SSL/TLS certificates
7. Set up proper logging and monitoring

## Commands

**View logs:**
```bash
docker-compose logs -f web
```

**Run Django management commands:**
```bash
docker-compose exec web python manage.py <command>
```

**Access Django shell:**
```bash
docker-compose exec web python manage.py shell
```

**Create superuser:**
```bash
docker-compose exec web python manage.py createsuperuser
```

**Load catalog data manually:**
```bash
docker-compose exec web python manage.py load_catalog
```


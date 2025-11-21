# Security and Secrets Management

This document describes how secrets are managed in the Rxinox project.

## Overview

The application is designed to run **without any secrets** by default, using SQLite as the database and development-friendly defaults.

## Secrets Configuration

### Files Containing Secrets

The following files contain sensitive information and are **excluded from version control** via `.gitignore`:

- `.env` - Environment variables with secrets (SECRET_KEY, database passwords, etc.)
- `.env.local` - Local environment overrides
- `catalog-*.csv` - Product catalog data files
- `db.sqlite3` - SQLite database file
- Any files matching patterns in `.gitignore`

### Template Files

The following template files are **included in version control** to show the expected structure:

- `.env.example` - Template for environment variables
- `catalog.example.csv` - Template showing expected CSV structure

## Default Configuration

### Without .env File (Development)

The application runs with **zero secrets required**:

- **Database**: SQLite (default, no configuration needed)
- **SECRET_KEY**: Uses insecure default (`django-insecure-change-this-in-production`) - **only for development**
- **DEBUG**: `True` by default
- **ALLOWED_HOSTS**: `localhost,127.0.0.1` by default

**To run the app without any setup:**
```bash
python manage.py migrate
python manage.py runserver
```

### With .env File (Production/Docker)

Create `.env` from `.env.example` and configure:

```bash
cp .env.example .env
# Edit .env with your values
```

Required for production:
- **SECRET_KEY**: Generate a secure secret key
- **DEBUG**: Set to `False`
- **ALLOWED_HOSTS**: Add your domain(s)

Optional for PostgreSQL:
- **DATABASE**: Set to `postgres`
- **POSTGRES_DB**, **POSTGRES_USER**, **POSTGRES_PASSWORD**: Database credentials

## Database Configuration

### SQLite (Default)

No configuration required. Works out of the box:

```bash
# No .env file needed
python manage.py migrate
python manage.py runserver
```

### PostgreSQL

Requires `.env` file with:

```env
DATABASE=postgres
POSTGRES_DB=your_db_name
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
SQL_HOST=db  # or localhost for local
SQL_PORT=5432
```

## Catalog File

The product catalog CSV file (`catalog-2025.csv`) is excluded from git because it contains proprietary product data. 

Use `catalog.example.csv` as a template to understand the expected structure.

To load your catalog:
1. Place your catalog CSV file in the project root (e.g., `catalog-2025.csv`)
2. Run: `python manage.py load_catalog`

## Security Checklist

Before committing:

- [ ] Verify `.env` is in `.gitignore` (it should be)
- [ ] Verify `.env.example` exists and contains no real secrets
- [ ] Verify `catalog-*.csv` files are in `.gitignore`
- [ ] Verify `db.sqlite3` is in `.gitignore`
- [ ] Verify no hardcoded secrets in source code
- [ ] Verify `SECRET_KEY` defaults to insecure value (development only)

## Production Deployment

When deploying to production:

1. **Generate a secure SECRET_KEY:**
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

2. **Set DEBUG=False** in `.env`

3. **Configure ALLOWED_HOSTS** with your domain

4. **Use PostgreSQL** with secure credentials

5. **Set up proper email configuration** if using email features

6. **Use environment variables or secret management** (never commit `.env`)


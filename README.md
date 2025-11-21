# Rxinox Django Project

A Django web application with a landing page and reusable header/footer templates.

## Features

- Landing page with modern, responsive design
- Reusable base template with header and footer
- SQLite database (default)
- Static files configured for CSS and other assets

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Load catalog data (optional):
```bash
# Copy catalog.example.csv to catalog-2025.csv (or your preferred name)
cp catalog.example.csv catalog-2025.csv
# Edit catalog-2025.csv with your product data
# Then load it into the database:
python manage.py load_catalog
```

6. Create a superuser (optional, for admin access):
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

8. Visit http://127.0.0.1:8000/ in your browser.

## Configuration

### Default Setup (No Secrets Required)

The application is designed to run **without any configuration files or secrets** by default:

- **Database**: Uses SQLite (no setup needed)
- **SECRET_KEY**: Uses development default (insecure, only for development)
- **DEBUG**: Enabled by default
- **ALLOWED_HOSTS**: Set to localhost

Just run migrations and start the server - no `.env` file needed for development!

### Production Setup

For production or Docker deployment, create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your production values:
# - Generate a secure SECRET_KEY
# - Set DEBUG=False
# - Configure ALLOWED_HOSTS
# - Optionally configure PostgreSQL (set DATABASE=postgres)
```

See [SECURITY.md](SECURITY.md) for detailed security and secrets management information.

## Project Structure

```
rxinox/
├── manage.py
├── requirements.txt
├── rxinox/              # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── pages/               # Main app
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── apps.py
│   └── templates/
│       └── pages/
│           ├── base.html      # Base template with header/footer
│           └── landing.html   # Landing page
└── static/              # Static files
    └── css/
        └── style.css
```

## Template Structure

The project uses Django's template inheritance:
- `base.html`: Contains the header and footer that will be reused across all pages
- `landing.html`: Extends `base.html` and provides the landing page content

## Next Steps

- Add user authentication
- Add more pages that extend the base template
- Customize the design and content


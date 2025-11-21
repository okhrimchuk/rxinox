# Rxinox Django E-Commerce Catalog

> **⚠️ Disclaimer:** This project was developed using Cursor AI with zero manual coding and is an experimental project. The code may not work as expected, may contain bugs, and has not been thoroughly tested. Use at your own risk.

A Django-based e-commerce catalog application for browsing products, managing a shopping cart, and placing orders.

## Features

- **Product Catalog**: Browse products organized by categories
- **Category Pages**: View all products within a specific category
- **Product Details**: Detailed product pages with image sliders and descriptions
- **Shopping Cart**: Session-based shopping cart with quantity management
- **Checkout Flow**: Complete checkout process with contact information and order summary
- **Catalog Management**: Load product catalog from CSV files
- **Responsive Design**: Modern, mobile-friendly interface
- **Image Management**: Support for multiple product images with automatic downloads
- **Search Bar**: Search functionality in header (ready for implementation)
- **SQLite Database** (default) - no secrets required for development
- **Docker Support**: Full containerization with Docker Compose

## Setup

### Quick Start (Development)

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Load catalog data (optional):**
   ```bash
   # Copy catalog.example.csv to catalog-2025.csv (or your preferred name)
   cp catalog.example.csv catalog-2025.csv
   # Edit catalog-2025.csv with your product data
   # Then load it into the database:
   python manage.py load_catalog
   ```

5. **Create a superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Visit http://127.0.0.1:8000/ in your browser.**

### Docker Setup

For Docker deployment, see [DOCKER.md](DOCKER.md) for detailed instructions.

Quick start with Docker:
```bash
cp .env.example .env
# Edit .env with your configuration
docker-compose up --build
```

### Render.com Deployment

For deploying to Render.com, see [RENDER.md](RENDER.md) for detailed instructions.

Quick deploy with Render:
1. Push your code to GitHub/GitLab/Bitbucket
2. Create a new Web Service in Render
3. Connect your repository
4. Render will automatically detect `render.yaml` configuration

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

## Application Structure

### Pages and Routes

- **Landing Page** (`/`): Displays product categories with images
- **Category Page** (`/categoria/<category-slug>/`): Lists all products in a category
- **Product Page** (`/categoria/<category-slug>/<product-slug>/`): Product details with image slider
- **Shopping Cart** (`/carrito/`): View and manage cart items
- **Checkout** (`/checkout/`): Enter contact information
- **Order Summary** (`/resumen-pedido/`): Review order before submission
- **Order Success** (`/pedido-exitoso/`): Order confirmation page

### Catalog Management

The application loads product data from CSV files. Use `catalog.example.csv` as a template for the expected structure.

**Management Commands:**
- `python manage.py load_catalog`: Load products from `catalog-2025.csv`

The CSV file should include columns for:
- Product code, name, price, description
- Category (full path format: "Category > Subcategory > Sub-subcategory")
- Images (supports up to 15 image URLs)
- Additional metadata (barcode, weight, producer, stock, etc.)

## Project Structure

```
rxinox/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── docker-entrypoint.sh
├── wait_for_db.py
├── .env.example              # Environment variables template
├── catalog.example.csv       # Catalog CSV template
├── rxinox/                   # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── pages/                    # Main app
│   ├── __init__.py
│   ├── models.py             # Category and Product models
│   ├── views.py              # View functions
│   ├── urls.py               # URL patterns
│   ├── apps.py
│   ├── admin.py              # Django admin configuration
│   ├── context_processors.py # Cart context processor
│   ├── management/
│   │   └── commands/
│   │       ├── load_catalog.py        # Load products from CSV
│   │       └── download_category_images.py  # Download category images
│   ├── migrations/           # Database migrations
│   └── templates/
│       └── pages/
│           ├── base.html          # Base template with header/footer
│           ├── landing.html       # Landing page (categories)
│           ├── category.html      # Category page (products)
│           ├── product.html       # Product detail page
│           ├── cart.html          # Shopping cart
│           ├── checkout.html      # Checkout form
│           ├── order_summary.html # Order summary
│           └── order_success.html # Order confirmation
├── static/                   # Static files
│   ├── css/
│   │   └── style.css
│   └── images/
│       ├── logo.png
│       └── loader.svg
└── media/                    # User uploaded files (created at runtime)
```

## Key Features Explained

### Session-Based Shopping Cart

The shopping cart is stored in the user's session, meaning:
- No user authentication required
- Cart persists during the browser session
- Cart counter automatically updates in header
- Items can be added, updated, or removed

### Image Management

- Products support multiple images (stored as JSON array)
- First image is used as primary image
- Category images are automatically derived from first product image in category
- Images can be loaded from URLs or stored locally

### Checkout Process

1. **Cart Page**: User reviews items and quantities
2. **Checkout Page**: User enters contact information
3. **Order Summary**: User reviews order and contact details
4. **Order Success**: Confirmation with order details

## Dependencies

- **Django** (>=5.0,<6.0): Web framework
- **Pillow** (>=10.0.0): Image processing
- **requests** (>=2.31.0): HTTP library for image downloads
- **psycopg2-binary** (>=2.9.0): PostgreSQL adapter (for Docker)
- **python-decouple** (>=3.8): Environment variable management

## Documentation

- **[DOCKER.md](DOCKER.md)**: Docker setup and deployment instructions
- **[SECURITY.md](SECURITY.md)**: Security and secrets management guide
- **[catalog.example.csv](catalog.example.csv)**: Example CSV structure for product catalog

## Development

### Running Tests

```bash
python manage.py test
```

### Accessing Admin Panel

1. Create a superuser: `python manage.py createsuperuser`
2. Visit: http://127.0.0.1:8000/admin/

### Database Management

**SQLite (default):**
- Database file: `db.sqlite3`
- No configuration needed

**PostgreSQL (optional):**
- Set `DATABASE=postgres` in `.env`
- Configure PostgreSQL credentials in `.env`
- See `.env.example` for reference

## License

[Add your license here]

# Deploying to Render.com

> **⚠️ Disclaimer:** This project was developed using Cursor AI with zero manual coding and is an experimental project. The deployment configuration may not work as expected, may contain bugs, and has not been thoroughly tested. Use at your own risk.

This guide explains how to deploy the Rxinox Django application to Render.com.

## Prerequisites

- A Render.com account (free tier available)
- A Git repository (GitHub, GitLab, or Bitbucket) with your code
- Basic understanding of environment variables

## Quick Deploy (Using render.yaml)

The project includes a `render.yaml` file for easy deployment:

1. **Push your code to GitHub/GitLab/Bitbucket**

2. **In Render Dashboard:**
   - Click "New" → "Blueprint"
   - Connect your repository
   - Render will detect the `render.yaml` file

3. **Configure Environment Variables:**
   - Set `SECRET_KEY`: Generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
   - Update `ALLOWED_HOSTS` in `render.yaml` with your actual service URL
   - Render will automatically set `DATABASE_URL` from the database service

4. **Deploy:**
   - Render will automatically create the web service and database
   - Wait for the build to complete

## Manual Deploy (Step by Step)

### Step 1: Create PostgreSQL Database

1. In Render Dashboard, click "New" → "PostgreSQL"
2. Name it `rxinox-db` (or your preferred name)
3. Select the free plan
4. Note the **Internal Database URL** (you'll need this later)

### Step 2: Create Web Service

1. Click "New" → "Web Service"
2. Connect your Git repository
3. Configure the service:

   **Basic Settings:**
   - **Name**: `rxinox-django` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (if repo root)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     bash render-start.sh
     ```
   
   **Note:** The startup script handles static files collection and migrations.
   Background jobs (catalog loading, image downloading) run automatically after the server starts.

### Step 3: Configure Environment Variables

In the Web Service settings, add these environment variables:

**Required:**
- `SECRET_KEY`: Generate a secure Django secret key:
  ```bash
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Your Render service URL (e.g., `rxinox-django.onrender.com`)
- `DATABASE_URL`: Copy from your PostgreSQL database service (Render provides this automatically if linked)

**Optional (for database):**
- `DATABASE`: Set to `postgres` (optional, DATABASE_URL takes precedence)
- `POSTGRES_DB`: Database name (from DATABASE_URL if set)
- `POSTGRES_USER`: Database user (from DATABASE_URL if set)
- `POSTGRES_PASSWORD`: Database password (from DATABASE_URL if set)

### Step 4: Link Database to Web Service

1. In your Web Service settings
2. Go to "Environment" tab
3. Click "Link Database"
4. Select your PostgreSQL database
5. Render will automatically add `DATABASE_URL` environment variable

### Step 5: Deploy

1. Click "Create Web Service" or "Manual Deploy"
2. Wait for the build to complete
3. Check build logs for any errors

### Step 6: Run Migrations

After deployment, run database migrations:

1. In Render Dashboard, go to your Web Service
2. Click "Shell" tab
3. Run:
   ```bash
   python manage.py migrate
   ```

### Step 7: Load Catalog Data (Optional)

If you have catalog data to load:

1. Upload your `catalog-2025.csv` file to Render
2. Use the Shell tab to run:
   ```bash
   python manage.py load_catalog
   ```

Or use a scheduled job to load data automatically.

### Step 8: Create Superuser (Optional)

To access Django admin:

1. Use the Shell tab:
   ```bash
   python manage.py createsuperuser
   ```
2. Follow the prompts to create an admin user

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | Yes | Django secret key | (Generated string) |
| `DEBUG` | Yes | Debug mode (False for production) | `False` |
| `ALLOWED_HOSTS` | Yes | Comma-separated allowed hosts | `rxinox-django.onrender.com` |
| `DATABASE_URL` | Yes* | PostgreSQL connection string | (Auto-provided by Render) |
| `DATABASE` | No | Database type (`postgres` or `sqlite`) | `postgres` |

*Required if using PostgreSQL (recommended for production)

## Important Notes

### Static Files

- Static files are automatically collected during build using `collectstatic`
- WhiteNoise middleware serves static files (no additional configuration needed)
- Static files are compressed and cached for better performance

### Media Files

- Media files (user uploads) are stored in the container's filesystem
- **Warning**: Files will be lost on container restart (Render free tier)
- For production, consider using AWS S3, Cloudinary, or similar service

### Database

- Render provides PostgreSQL databases
- Database credentials are automatically available via `DATABASE_URL`
- The app automatically detects and uses `DATABASE_URL` if present
- SQLite is used as fallback if no PostgreSQL is configured

### Catalog File

- The catalog CSV file is not included in the repository (gitignored)
- Upload it manually after deployment or use a build script
- Consider storing it in a cloud storage service for easier access

### Auto-Deploy

- Render automatically deploys on every push to the connected branch
- Enable "Auto-Deploy" in service settings
- Use branch-specific deployments for staging/production

## Troubleshooting

### Build Fails

- Check build logs for specific error messages
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### Application Won't Start

- Check start command is correct: `gunicorn rxinox.wsgi:application`
- Verify `SECRET_KEY` is set
- Check `ALLOWED_HOSTS` includes your Render URL
- Review application logs in Render dashboard

### Database Connection Errors

- Verify `DATABASE_URL` is set correctly
- Check database is linked to web service
- Ensure database service is running
- Verify database credentials are correct

### Static Files Not Loading

- Ensure `collectstatic` runs during build
- Check `STATIC_ROOT` is set correctly in settings
- Verify WhiteNoise middleware is in `MIDDLEWARE` list
- Check static files exist in `staticfiles` directory

### 500 Internal Server Error

- Enable `DEBUG=True` temporarily to see error details
- Check application logs in Render dashboard
- Verify all environment variables are set
- Check database migrations have been run

## Free Tier Limitations

- **Spins down after 15 minutes of inactivity** (Free tier)
- Service may take 30-60 seconds to wake up
- Limited database storage
- No persistent file storage for media files

## Production Recommendations

For production deployments:

1. **Upgrade to paid plan** for always-on service
2. **Use external storage** for media files (AWS S3, Cloudinary)
3. **Set up monitoring** and logging
4. **Configure custom domain** in Render settings
5. **Enable SSL/TLS** (automatic on Render)
6. **Set up backup strategy** for database
7. **Configure email** for order notifications
8. **Use environment-specific settings** (staging/production)

## Resources

- [Render Django Deployment Guide](https://render.com/docs/deploy-django)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)


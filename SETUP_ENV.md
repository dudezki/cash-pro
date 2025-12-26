# Environment Setup Guide

## Creating .env File

Create a `.env` file in the root directory with the following content:

```env
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=cash_pro_control
POSTGRES_PORT=5432

# Super Admin Credentials (REQUIRED - Change these!)
SUPER_ADMIN_USERNAME=admin@cashpro.com
SUPER_ADMIN_PASSWORD=YourSecurePassword123!

# Application Security
SECRET_KEY=your-secret-key-change-in-production-use-random-string-here

# CORS Configuration
CORS_ORIGINS=http://localhost:5173
```

## Important Notes

1. **SUPER_ADMIN_USERNAME**: This will be the email address you use to login as super admin
2. **SUPER_ADMIN_PASSWORD**: Choose a strong password for the super admin account
3. **SECRET_KEY**: Generate a random string for production (you can use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

## After Creating .env

1. Restart Docker Compose:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

2. Check logs to verify super admin was created:
   ```bash
   docker-compose logs backend | grep -i "super admin"
   ```

3. You should see: `Super admin 'admin@cashpro.com' created successfully`

4. Login at http://localhost:5173/login with your SUPER_ADMIN_USERNAME and SUPER_ADMIN_PASSWORD


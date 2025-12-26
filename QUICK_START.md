# Quick Start Guide

## Prerequisites
- Docker and Docker Compose installed
- Node.js 18+ installed (for frontend)

## Step 1: Create .env file

Create a `.env` file in the root directory with the following content:

```env
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=cash_pro_control
POSTGRES_PORT=5432

# Super Admin Credentials
SUPER_ADMIN_USERNAME=admin@example.com
SUPER_ADMIN_PASSWORD=change_me_in_production

# Application Security
SECRET_KEY=your-secret-key-change-in-production-use-random-string

# CORS Configuration
CORS_ORIGINS=http://localhost:5173
```

**Important**: Change `SUPER_ADMIN_PASSWORD` and `SECRET_KEY` to secure values!

## Step 2: Start Backend Services

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Build and start the FastAPI backend
- Automatically create the super admin account

Wait for services to be healthy (check with `docker-compose ps`)

## Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Step 4: Start Frontend Development Server

```bash
cd frontend
npm run dev
```

## Step 5: Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

## Testing the Setup

### 1. Test API Health
```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

### 2. Test Super Admin Login
1. Go to http://localhost:5173/login
2. Use the credentials from `.env`:
   - Email: `SUPER_ADMIN_USERNAME` value
   - Password: `SUPER_ADMIN_PASSWORD` value

### 3. Register a New User
1. Go to http://localhost:5173/register
2. Fill in the registration form
3. This will create:
   - A new Person account
   - A new Company
   - A Subscription (trial)
   - A tenant database (automatically)

### 4. Test Super Admin Features
1. Login as super admin
2. Navigate to Admin → Users
3. You should see all registered users
4. Try "Act as User" to impersonate

### 5. Test RBAC
1. Login as a regular user
2. Navigate to Settings → Roles
3. View available roles and permissions
4. Create a new role (if you're admin/owner)

## Troubleshooting

### Backend not starting
- Check logs: `docker-compose logs backend`
- Verify `.env` file exists and has all required variables
- Check PostgreSQL is healthy: `docker-compose ps`

### Frontend can't connect to backend
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS_ORIGINS in `.env` matches frontend URL
- Check browser console for errors

### Database connection errors
- Verify PostgreSQL container is running: `docker-compose ps postgres`
- Check database credentials in `.env`
- Check backend logs: `docker-compose logs backend`

### Super admin not created
- Check backend logs: `docker-compose logs backend | grep -i admin`
- Verify SUPER_ADMIN_USERNAME and SUPER_ADMIN_PASSWORD are set in `.env`
- Try restarting: `docker-compose restart backend`

## Useful Commands

```bash
# View all logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild and start
docker-compose up -d --build

# View database
docker-compose exec postgres psql -U postgres -d cash_pro_control

# View backend shell
docker-compose exec backend bash
```


# Cash Pro - Multi-Tenant SaaS Application

A complete multi-tenant SaaS application with user authentication, role-based access control (RBAC), and separate database per tenant architecture.

## Features

- **User Authentication**: Registration, login, logout with session-based authentication
- **Multi-Tenant Architecture**: Separate database per company for maximum data isolation
- **RBAC System**: Company-level roles and resource-level permissions
- **Super Admin**: User impersonation and system administration
- **Vue 3 Frontend**: Modern UI with Framer Motion-like animations
- **FastAPI Backend**: High-performance Python backend with PostgreSQL

## Architecture

- **Control Database**: Shared PostgreSQL database for People, Companies, Subscriptions
- **Tenant Databases**: One PostgreSQL database per company for isolated data
- **Session Management**: HTTP-only cookies for secure session handling
- **RBAC**: Role-based and resource-level permission system

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

## Setup

1. **Clone the repository**

2. **Create `.env` file** (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit `.env` and set:
- `SUPER_ADMIN_USERNAME`: Super admin email
- `SUPER_ADMIN_PASSWORD`: Super admin password
- Database credentials

3. **Start services with Docker Compose**:
```bash
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Initialize super admin account
- Start FastAPI backend on port 8000

4. **Setup Frontend**:
```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:5173`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user
- `POST /api/auth/switch-company` - Switch company context

### Admin (Super Admin Only)
- `GET /api/admin/users` - List all users
- `GET /api/admin/companies` - List all companies
- `POST /api/admin/impersonate/{user_id}` - Impersonate user
- `POST /api/admin/stop-impersonate` - Stop impersonating
- `POST /api/admin/companies/{company_id}/create-db` - Create tenant database

### RBAC
- `GET /api/rbac/roles` - Get roles for current company
- `POST /api/rbac/roles` - Create role
- `GET /api/rbac/permissions` - Get permissions
- `POST /api/rbac/assign-role` - Assign role to user

## Database Schema

### Control Database
- `people` - User accounts
- `companies` - Company/tenant information
- `subscriptions` - Subscription plans
- `person_companies` - User-company relationships
- `sessions` - Active sessions
- `company_settings` - Company configuration

### Tenant Database (per company)
- `roles` - Role definitions
- `permissions` - Permission definitions
- `role_permissions` - Role-permission mappings
- `user_roles` - User-role assignments
- `resource_permissions` - Resource-level permissions

## Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Super Admin

On first Docker Compose build, a super admin account is automatically created using credentials from `.env`:
- `SUPER_ADMIN_USERNAME`
- `SUPER_ADMIN_PASSWORD`

Super admin can:
- View all users and companies
- Impersonate any user
- Create tenant databases manually
- Access all resources

## License

MIT


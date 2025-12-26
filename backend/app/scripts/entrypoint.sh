#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h ${POSTGRES_HOST:-postgres} -U ${POSTGRES_USER:-postgres} 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing commands"

# Add username column to database if it doesn't exist
echo "Adding username column to database..."
python -m app.scripts.add_username_column || echo "Warning: Username column migration failed"

# Run super admin initialization
echo "Initializing super admin..."
python -m app.scripts.init_super_admin || echo "Warning: Super admin initialization failed"

# Add usernames to existing users
echo "Adding usernames to existing users..."
python -m app.scripts.add_username_to_existing_users || echo "Warning: Username update failed"

# Seed financial modules
echo "Seeding financial modules..."
python -m app.scripts.seed_modules || echo "Warning: Module seeding failed"

# Seed subscription plans
echo "Seeding subscription plans..."
python -m app.scripts.seed_subscription_plans || echo "Warning: Subscription plan seeding failed"

# Run database migrations (if using Alembic)
# alembic upgrade head

# Start the application
echo "Starting FastAPI application..."
exec "$@"


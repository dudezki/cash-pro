from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.models import person, company, subscription, person_company, session, company_setting, subscription_plan
from app.api import auth, admin, rbac

# Create database tables
person.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cash Pro API",
    description="Multi-tenant SaaS application with RBAC",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(rbac.router, prefix="/api/rbac", tags=["rbac"])

# Import and include new routers
from app.api import company, subscription, subscription_plan
app.include_router(company.router, prefix="/api/company", tags=["company"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["subscription"])
app.include_router(subscription_plan.router, prefix="/api/admin", tags=["admin-subscription-plans"])

@app.get("/")
async def root():
    return {"message": "Cash Pro API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}


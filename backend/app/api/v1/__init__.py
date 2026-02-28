from fastapi import APIRouter
from app.api.v1 import auth, users, issues, ai, contributions, admin, privacy

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth.router)

# Include user management routes
api_router.include_router(users.router)

# Include issue discovery routes
api_router.include_router(issues.router)

# Include AI service routes
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])

# Include contribution routes
api_router.include_router(contributions.router)

# Include admin routes
api_router.include_router(admin.router)

# Include privacy/GDPR routes
api_router.include_router(privacy.router)

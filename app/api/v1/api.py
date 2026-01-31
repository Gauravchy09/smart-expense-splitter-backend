from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, groups, expenses, ocr, settlements, recurring, notifications

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
api_router.include_router(settlements.router, prefix="/settlements", tags=["settlements"])
api_router.include_router(recurring.router, prefix="/recurring", tags=["recurring"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

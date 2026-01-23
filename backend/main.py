"""
MarketMate FastAPI Backend Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from backend.config import settings
from backend.routes import auth, dashboard, customers, orders, items, shipping, payments, reviews, rewards

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="MarketMate E-commerce Management API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    swagger_ui_cdn_url="https://unpkg.com/swagger-ui-dist@3",
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(items.router)
app.include_router(shipping.router)
app.include_router(payments.router)
app.include_router(reviews.router)
app.include_router(rewards.router)

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/")
async def root():
    """API Root endpoint"""
    return {
        "message": "Welcome to MarketMate API",
        "version": settings.VERSION,
        "docs": "/api/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Global exception handler - DISABLED FOR DEBUGGING
# @app.exception_handler(Exception)
# async def global_exception_handler(request, exc):
#     """Global exception handler"""
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "An internal server error occurred"}
#     )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

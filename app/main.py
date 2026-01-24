from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.session import init_db
from app.routes import employees, attendance

# Create FastAPI app
app = FastAPI(title=settings.app_name, debug=settings.debug)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization warning: {e}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://hrms-lite-frontend-navy.vercel.app",
        "https://hrms-lite-frontend-git-master-harshitsingh2035-2411s-projects.vercel.app",
        "https://hrms-lite-frontend-2fuko3j5k-harshitsingh2035-2411s-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(employees.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": str(__import__('datetime').datetime.utcnow())}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "HRMS Lite API - Ready to use"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)

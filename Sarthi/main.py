from fastapi import FastAPI
from orchestrator.stage_router import router as stage_router
from routers.users import router as user_router
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Reflection Platform API",
    description="API for managing reflection workflows",
    version="1.0.0"
)

# Include routers
app.include_router(user_router, prefix="/api")
app.include_router(stage_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Reflection Platform API is running!"}

@app.get("/test")
async def serve_test_page():
    return FileResponse("test.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "reflection-platform"}


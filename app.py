from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.ads import router as ads_router
from routers.credits import router as credits_router
from routers.payments import router as payments_router

app = FastAPI(title="AdGen Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ads_router, prefix="/ads", tags=["ads"])
app.include_router(credits_router, prefix="/credits", tags=["credits"])
app.include_router(payments_router, prefix="/payments", tags=["payments"])

@app.get("/")
def read_root():
    return {"message": "AdGen Backend API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"} 
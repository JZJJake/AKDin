
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import stocks, backtest

app = FastAPI(title="Stock Strategy Platform API", version="1.0.0")

# Configure CORS
# For development, allowing all origins is convenient. In production, restrict this.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(stocks.router, prefix="/api/v1", tags=["stocks"])
app.include_router(backtest.router, prefix="/api/v1", tags=["backtest"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Stock Strategy Platform API"}

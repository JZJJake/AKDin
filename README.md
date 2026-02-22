
# Stock Strategy Platform (智能量化投研平台)

A full-stack quantitative trading platform featuring strategy backtesting, stock screening, and automated monitoring.

## Features

- **Market Center (行情中心)**: Real-time market data with professional charts (K-line, Volume, MACD, KDJ).
- **Strategy Lab (策略研究室)**: Python-based strategy editor with backtesting engine and equity curve visualization.
- **Smart Screener (智能选股)**: Scan the market for buy signals using custom strategies.
- **Auto-Monitor (自动盯盘)**: WeChat push notifications for real-time signals.

## Requirements

- Python 3.9+
- Node.js 16+ (Compatible with Windows Server 2012 R2)
- Redis (Required for Celery tasks)
- PostgreSQL (Recommended) or SQLite (Default)

## Quick Start (One-Click)

1.  **Install Backend Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Frontend Dependencies**:
    ```bash
    cd frontend
    npm install
    cd ..
    ```

3.  **Start All Services**:
    Run the unified startup script:
    ```bash
    python start.py
    ```
    This will launch:
    - Backend API: http://localhost:8000
    - Frontend UI: http://localhost:5173
    - Celery Worker & Scheduler

## Manual Startup

If you prefer running services individually:

1.  **Backend**:
    ```bash
    uvicorn app.main:app --reload
    ```

2.  **Frontend**:
    ```bash
    cd frontend
    npm run dev
    ```

3.  **Celery Worker**:
    ```bash
    # Windows
    celery -A app.worker.celery_app worker --loglevel=info -P solo

    # Linux/Mac
    celery -A app.worker.celery_app worker --loglevel=info
    ```

4.  **Celery Beat**:
    ```bash
    celery -A app.worker.celery_app beat --loglevel=info
    ```

## Configuration

Edit `app/core/config.py` or use environment variables:
- `DATABASE_URL`: Database connection string.
- `REDIS_URL`: Redis connection string.
- `PUSH_TOKEN`: PushPlus token for WeChat notifications.

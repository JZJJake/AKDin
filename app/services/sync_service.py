
import pandas as pd
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import inspect
from app.core.database import SessionLocal, engine
from app.models.stock import StockBasic
from app.services.data_fetcher import DataFetcher

def update_stock_list():
    """
    Updates the stock list in the database using data from AkShare.
    Uses bulk upsert for performance.
    """
    print("Fetching stock list from AkShare...")
    try:
        df = DataFetcher.get_stock_list_data()
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return

    if df is None or df.empty:
        print("No data received.")
        return

    print(f"Received {len(df)} records. Preparing for database update...")

    # Map DataFrame columns to model fields
    # Expected columns from stock_zh_a_spot_em: "代码", "名称", ...
    records = []
    for _, row in df.iterrows():
        record = {
            "symbol": str(row["代码"]),
            "name": str(row["名称"]),
            # "industry": row.get("行业"), # If available in future
            # "list_date": row.get("上市日期") # If available in future
        }
        records.append(record)

    db = SessionLocal()
    try:
        # Check dialect to decide on upsert strategy
        dialect = inspect(engine).dialect.name

        if dialect == 'postgresql':
            stmt = pg_insert(StockBasic).values(records)
            stmt = stmt.on_conflict_do_update(
                index_elements=[StockBasic.symbol],
                set_={
                    "name": stmt.excluded.name,
                    # Update other fields if we had them
                }
            )
            db.execute(stmt)
        else:
            # Fallback for SQLite or other DBs (e.g. during local testing)
            # SQLite supports ON CONFLICT from 3.24, but via sqlite dialect
            # For simplicity in non-pg environments, we can use merge or delete-insert
            # Using merge is slower but safe. Or we can just try bulk_save_objects if we assume clean slate.
            # But let's try to be smart.

            # Simple approach for non-PG:
            # 1. Get existing symbols
            existing_symbols = {s[0] for s in db.query(StockBasic.symbol).all()}

            new_records = []
            update_records = []

            for r in records:
                if r['symbol'] in existing_symbols:
                    update_records.append(r)
                else:
                    new_records.append(StockBasic(**r))

            if new_records:
                db.bulk_save_objects(new_records)

            if update_records:
                db.bulk_update_mappings(StockBasic, update_records)

        db.commit()
        print("Stock list updated successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error updating database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_stock_list()

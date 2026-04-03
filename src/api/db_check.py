from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from sqlalchemy import text

router = APIRouter()

@router.get("/api/db-status")
async def db_status(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        return {"status": "connected", "test": result.scalar()}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

import os
import subprocess

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/backup",
    tags=["Backup"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "").replace(
    "postgresql+psycopg2://",
    "postgresql://",
    1,
)


@router.get("/download")
def download_backup():
    if not DATABASE_URL:
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL not set",
        )

    backup_file = "gym_backup.sql"

    try:
        result = subprocess.run(
            ["pg_dump", DATABASE_URL, "-f", backup_file],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Backup operation timed out",
        )
    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Could not execute pg_dump",
        )

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail="Backup failed. Check server logs.",
        )

    return FileResponse(
        path=backup_file,
        filename="gym_backup.sql",
        media_type="application/sql",
    )

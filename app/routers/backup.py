import os
import subprocess
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/backup",
    tags=["Backup"]
)

DATABASE_URL = os.getenv("DATABASE_URL")

@router.get("/download")
def download_backup():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL not set")

    backup_file = "gym_backup.sql"

    result = subprocess.run(
        ["pg_dump", DATABASE_URL, "-f", backup_file],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"Backup failed: {result.stderr}"
        )

    return FileResponse(
        path=backup_file,
        filename="gym_backup.sql",
        media_type="application/sql"
    )

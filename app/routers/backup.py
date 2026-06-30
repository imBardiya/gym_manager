from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/backup",
    tags=["Backup"]
)


@router.get("/download")
def download_backup():

    return FileResponse(
        path="gym.db",
        filename="gym_backup.db",
        media_type="application/octet-stream"
    )
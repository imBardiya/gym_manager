from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import GymSession
from fastapi import Request
from fastapi.responses import RedirectResponse
from app.core.templates import templates
from app.models import Student
from datetime import datetime
import jdatetime
from app.models.student_session import student_sessions


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

@router.get("/add")
def add_session_form(
    request: Request
):
    return templates.TemplateResponse(
        request=request,
        name="add_session.html"
    )

@router.post("/add")
def add_session(
    title: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    session_type: str = Form(...),
    db: Session = Depends(get_db)
):

    if session_type not in [
        "daily",
        "odd",
        "even"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid session type"
        )

    session = GymSession(
        title=title,
        start_time=start_time,
        end_time=end_time,
        session_type=session_type
    )

    db.add(session)

    db.commit()

    db.refresh(session)

    return RedirectResponse(
        url="/sessions",
        status_code=303
    )

@router.get("/{session_id}")
def session_detail(
    request: Request,
    session_id: int,
    db: Session = Depends(get_db)
):
    session = (
        db.query(GymSession)
        .filter(GymSession.id == session_id)
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # هم سانس‌های قدیمی و هم جدید
    students = (
        db.query(Student)
        .filter(
            (Student.session_id == session_id) |
            (Student.id.in_(
                db.query(student_sessions.c.student_id)
                .filter(student_sessions.c.session_id == session_id)
            ))
        )
        .order_by(Student.full_name)
        .all()
    )

    # حذف تکراری‌ها
    unique_students = list({s.id: s for s in students}.values())

    now = datetime.now()
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now)

    return templates.TemplateResponse(
        request=request,
        name="session_detail.html",
        context={
            "session": session,
            "students": unique_students,
            "now": now,
            "jalali_now": jalali_now
        }
    )

@router.get("/")
def list_sessions(
    request: Request,
    db: Session = Depends(get_db)
):

    sessions = (
        db.query(GymSession)
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="sessions.html",
        context={
            "sessions": sessions
        }
    )

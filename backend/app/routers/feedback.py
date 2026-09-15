"""
Feedback Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.models import UserFeedback
from app.schemas.schemas import FeedbackCreate

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("")
def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    obj = UserFeedback(
        route_id=feedback.route_id,
        rating=feedback.rating,
        comment=feedback.comment,
        user_email=feedback.user_email
    )
    db.add(obj)
    db.commit()
    return {"message": "Feedback submitted. Thank you!", "id": obj.id}

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database.session import get_db
from app.dependencies.auth_dependency import check_user_permissions
from app.models.user import User, UserRole
from app.models.submission import SubmissionStatus
from app.crud.submission_crud import submission_crud
from app.schemas.submission_schema import SubmissionCreate, SubmissionRead
from app.schemas.api_response import APIResponse, success_response
from app.core.decorators import standardize_response

router = APIRouter(prefix="/influencer/submissions", tags=["Influencer Submissions"])


@router.post("", response_model=APIResponse[SubmissionRead], status_code=201)
@standardize_response
def create_submission(
    *,
    db: Session = Depends(get_db),
    obj_in: SubmissionCreate,
    current_user: User = Depends(check_user_permissions(UserRole.influencer))
):
    submission = submission_crud.create(db=db, obj_in=obj_in, influencer_id=current_user.id)
    return success_response(
        data=SubmissionRead.model_validate(submission),
        message="Submission created successfully",
        status_code=201
    )


@router.get("", response_model=APIResponse[List[SubmissionRead]])
@standardize_response
def get_my_submissions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.influencer)),
    status: Optional[SubmissionStatus] = Query(None),
    from_date: Optional[datetime] = Query(None)
):
    submissions = submission_crud.get_by_influencer(
        db=db,
        influencer_id=current_user.id,
        status=status,
        from_date=from_date
    )
    return success_response(
        data=[SubmissionRead.model_validate(s) for s in submissions],
        message="Submissions retrieved successfully"
    )


@router.get("/{submission_id}", response_model=APIResponse[SubmissionRead])
@standardize_response
def get_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: int,
    current_user: User = Depends(check_user_permissions(UserRole.influencer))
):
    submission = submission_crud.get_by_id(db=db, submission_id=submission_id)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.influencer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this submission")

    return success_response(
        data=SubmissionRead.model_validate(submission),
        message="Submission retrieved successfully"
    )


@router.delete("/{submission_id}", status_code=204)
def delete_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: int,
    current_user: User = Depends(check_user_permissions(UserRole.influencer))
):
    submission_crud.delete(db=db, submission_id=submission_id, influencer_id=current_user.id)
    return None

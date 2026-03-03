from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth_dependency import check_user_permissions
from app.models.user import User, UserRole
from app.models.submission import SubmissionStatus
from app.crud.submission_crud import submission_crud
from app.schemas.submission_schema import (
    SubmissionRead,
    SubmissionUpdate,
    SubmissionReject
)
from app.schemas.api_response import APIResponse, success_response
from app.core.decorators import standardize_response

router = APIRouter(
    prefix="/admin/influencer/submissions",
    tags=["Admin - Influencer Submissions"]
)


@router.get("", response_model=APIResponse[List[SubmissionRead]])
@standardize_response
def get_all_submissions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_user_permissions(UserRole.admin)),
    status: Optional[SubmissionStatus] = Query(None),
    influencer_id: Optional[int] = Query(None),
    from_date: Optional[datetime] = Query(None)
):
    submissions = submission_crud.get_all(
        db=db,
        status=status,
        influencer_id=influencer_id,
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
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    submission = submission_crud.get_by_id(db=db, submission_id=submission_id)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return success_response(
        data=SubmissionRead.model_validate(submission),
        message="Submission retrieved successfully"
    )


@router.put("/{submission_id}/approve", response_model=APIResponse[SubmissionRead])
@standardize_response
def approve_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: int,
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    submission = submission_crud.approve(db=db, submission_id=submission_id)
    return success_response(
        data=SubmissionRead.model_validate(submission),
        message="Submission approved successfully"
    )


@router.put("/{submission_id}/reject", response_model=APIResponse[SubmissionRead])
@standardize_response
def reject_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: int,
    obj_in: SubmissionReject,
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    submission = submission_crud.reject(
        db=db,
        submission_id=submission_id,
        feedback=obj_in.feedback
    )
    return success_response(
        data=SubmissionRead.model_validate(submission),
        message="Submission rejected successfully"
    )


@router.put("/{submission_id}/edit", response_model=APIResponse[SubmissionRead])
@standardize_response
def edit_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: int,
    obj_in: SubmissionUpdate,
    current_user: User = Depends(check_user_permissions(UserRole.admin))
):
    submission = submission_crud.edit(db=db, submission_id=submission_id, obj_in=obj_in)
    return success_response(
        data=SubmissionRead.model_validate(submission),
        message="Submission edited successfully"
    )

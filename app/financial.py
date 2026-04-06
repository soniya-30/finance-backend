from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func

from app import models, database
from app.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/financial-records", tags=["Financial Records"])


# -------------------------
# DB session
# -------------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Get all records
# -------------------------
@router.get("/")
def get_records(
    user = Depends(require_roles(["admin", "analyst", "viewer"])),
    db: Session = Depends(get_db)
):
    if user.get("role") == "viewer":
        # viewer sees only their own records
        records = db.query(models.FinancialRecord).filter(
            models.FinancialRecord.user_id == int(user.get("sub")),
            models.FinancialRecord.is_deleted == False
        ).all()
    else:
        # admin and analyst see all records
        records = db.query(models.FinancialRecord).filter(
            models.FinancialRecord.is_deleted == False
        ).all()

    return records


# -------------------------
# Create a new record
# -------------------------
@router.post("/")
def create_record(
    record: dict,
    user = Depends(require_roles(["admin", "viewer"])),
    db: Session = Depends(get_db)
):
    new_record = models.FinancialRecord(
        user_id = record.get("user_id") if user.get("role") == "admin" else int(user.get("sub")),
        amount = record.get("amount"),
        description = record.get("description")
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return {"message": "Record created", "record_id": new_record.id}


# -------------------------
# Soft delete a record (admin only)
# -------------------------
@router.delete("/{record_id}")
def delete_record(
    record_id: int,
    user = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    record = db.query(models.FinancialRecord).filter(
        models.FinancialRecord.id == record_id,
        models.FinancialRecord.is_deleted == False
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    record.is_deleted = True
    db.commit()

    return {"message": "Record soft-deleted"}


# -------------------------
# Dashboard APIs
# -------------------------
@router.get("/dashboard/total-records")
def total_records(
    user = Depends(require_roles(["admin", "analyst"])),
    db: Session = Depends(get_db)
):
    count = db.query(models.FinancialRecord).filter(
        models.FinancialRecord.is_deleted == False
    ).count()

    return {"total_records": count}


@router.get("/dashboard/total-amount")
def total_amount(
    user = Depends(require_roles(["admin", "analyst"])),
    db: Session = Depends(get_db)
):
    total = db.query(func.sum(models.FinancialRecord.amount)).filter(
        models.FinancialRecord.is_deleted == False
    ).scalar()

    return {"total_amount": total or 0}


@router.get("/dashboard/user-summary")
def user_summary(
    user = Depends(require_roles(["admin", "analyst"])),
    db: Session = Depends(get_db)
):
    data = db.query(
        models.FinancialRecord.user_id,
        func.sum(models.FinancialRecord.amount)
    ).filter(
        models.FinancialRecord.is_deleted == False
    ).group_by(models.FinancialRecord.user_id).all()

    return [{"user_id": d[0], "total": d[1]} for d in data]
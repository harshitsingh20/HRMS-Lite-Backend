from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date as date_type

from app.database.session import get_db
from app.models.models import Employee, Attendance
from app.schemas.schemas import AttendanceCreate, AttendanceResponse

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def mark_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    """Mark attendance for an employee"""
    try:
        # Check if employee exists
        employee = db.query(Employee).filter(Employee.id == UUID(attendance.employee_id)).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        # Check for existing attendance record
        attendance_date = date_type.fromisoformat(attendance.date)
        existing = db.query(Attendance).filter(
            Attendance.employee_id == UUID(attendance.employee_id),
            Attendance.date == attendance_date
        ).first()

        if existing:
            # Update existing record
            existing.status = attendance.status
            db.commit()
            db.refresh(existing)
            return {
                "success": True,
                "message": "Attendance updated successfully",
                "data": existing.to_dict()
            }

        # Create new attendance record
        db_attendance = Attendance(
            employee_id=UUID(attendance.employee_id),
            date=attendance_date,
            status=attendance.status
        )
        db.add(db_attendance)
        db.commit()
        db.refresh(db_attendance)

        return {
            "success": True,
            "message": "Attendance marked successfully",
            "data": db_attendance.to_dict()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=dict)
async def get_all_attendance(date: str = Query(None), db: Session = Depends(get_db)):
    """Get all attendance records"""
    try:
        query = db.query(Attendance)

        if date:
            attendance_date = date_type.fromisoformat(date)
            query = query.filter(Attendance.date == attendance_date)

        records = query.order_by(Attendance.date.desc()).all()

        return {
            "success": True,
            "message": "Attendance records retrieved successfully",
            "data": [record.to_dict() for record in records],
            "total": len(records)
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/employee/{employee_id}", response_model=dict)
async def get_employee_attendance(employee_id: str, month: str = Query(None), db: Session = Depends(get_db)):
    """Get attendance records for a specific employee"""
    try:
        # Check if employee exists
        employee = db.query(Employee).filter(Employee.id == UUID(employee_id)).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        query = db.query(Attendance).filter(Attendance.employee_id == UUID(employee_id))

        if month:
            # Filter by month (YYYY-MM format)
            year, month_num = map(int, month.split("-"))
            query = query.filter(
                Attendance.date >= date_type(year, month_num, 1)
            )

        records = query.order_by(Attendance.date.desc()).all()

        return {
            "success": True,
            "message": "Attendance records retrieved successfully",
            "data": [record.to_dict() for record in records],
            "total": len(records)
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{attendance_id}", response_model=dict)
async def delete_attendance(attendance_id: str, db: Session = Depends(get_db)):
    """Delete an attendance record"""
    try:
        record = db.query(Attendance).filter(Attendance.id == UUID(attendance_id)).first()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        db.delete(record)
        db.commit()

        return {
            "success": True,
            "message": "Attendance record deleted successfully"
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid attendance ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

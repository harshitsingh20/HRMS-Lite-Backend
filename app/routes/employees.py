from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.database.session import get_db
from app.models.models import Employee
from app.schemas.schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee"""
    try:
        # Check for duplicate employee_id
        existing_emp = db.query(Employee).filter(Employee.employee_id == employee.employee_id).first()
        if existing_emp:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee ID already exists"
            )

        # Check for duplicate email
        existing_email = db.query(Employee).filter(Employee.email == employee.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        # Create new employee
        db_employee = Employee(
            employee_id=employee.employee_id,
            full_name=employee.full_name,
            email=employee.email,
            department=employee.department
        )
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)

        return {
            "success": True,
            "message": "Employee created successfully",
            "data": EmployeeResponse(**db_employee.to_dict())
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("", response_model=dict)
async def get_employees(db: Session = Depends(get_db)):
    """Get all employees"""
    try:
        employees = db.query(Employee).order_by(Employee.created_at.desc()).all()
        return {
            "success": True,
            "message": "Employees retrieved successfully",
            "data": [EmployeeResponse(**emp.to_dict()) for emp in employees],
            "total": len(employees)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{employee_id}", response_model=dict)
async def get_employee(employee_id: str, db: Session = Depends(get_db)):
    """Get employee by ID"""
    try:
        employee = db.query(Employee).filter(Employee.id == UUID(employee_id)).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        return {
            "success": True,
            "message": "Employee retrieved successfully",
            "data": EmployeeResponse(**employee.to_dict())
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid employee ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{employee_id}", response_model=dict)
async def update_employee(employee_id: str, employee_update: EmployeeUpdate, db: Session = Depends(get_db)):
    """Update employee"""
    try:
        employee = db.query(Employee).filter(Employee.id == UUID(employee_id)).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        # Check for duplicate email if email is being updated
        if employee_update.email and employee_update.email != employee.email:
            existing_email = db.query(Employee).filter(
                Employee.email == employee_update.email,
                Employee.id != UUID(employee_id)
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists"
                )

        # Update fields
        if employee_update.full_name:
            employee.full_name = employee_update.full_name
        if employee_update.email:
            employee.email = employee_update.email
        if employee_update.department:
            employee.department = employee_update.department

        employee.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(employee)

        return {
            "success": True,
            "message": "Employee updated successfully",
            "data": EmployeeResponse(**employee.to_dict())
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid employee ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{employee_id}", response_model=dict)
async def delete_employee(employee_id: str, db: Session = Depends(get_db)):
    """Delete employee"""
    try:
        employee = db.query(Employee).filter(Employee.id == UUID(employee_id)).first()
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )

        db.delete(employee)
        db.commit()

        return {
            "success": True,
            "message": "Employee deleted successfully"
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid employee ID format"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

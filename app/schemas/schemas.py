from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import date


class EmployeeBase(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str

    @field_validator("employee_id")
    @classmethod
    def employee_id_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Employee ID is required")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Full Name is required")
        return v

    @field_validator("department")
    @classmethod
    def department_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Department is required")
        return v


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AttendanceBase(BaseModel):
    employee_id: str
    date: str
    status: str

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v):
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ["Present", "Absent"]:
            raise ValueError("Status must be either Present or Absent")
        return v


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(BaseModel):
    id: str
    employee_id: str
    emp_id: str
    full_name: str
    date: str
    status: str
    created_at: str

    class Config:
        from_attributes = True

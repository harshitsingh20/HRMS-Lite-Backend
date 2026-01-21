from sqlalchemy import Column, String, DateTime, ForeignKey, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.session import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    department = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id),
            "employee_id": self.employee_id,
            "full_name": self.full_name,
            "email": self.email,
            "department": self.department,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("employee_id", "date", name="unique_employee_date"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    status = Column(String(50), nullable=False)  # "Present" or "Absent"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")

    def to_dict(self):
        return {
            "id": str(self.id),
            "employee_id": str(self.employee_id),
            "emp_id": self.employee.employee_id,
            "full_name": self.employee.full_name,
            "date": self.date.isoformat(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }

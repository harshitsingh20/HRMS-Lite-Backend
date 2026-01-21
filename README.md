# HRMS Lite - FastAPI Backend

A modern, production-ready Human Resource Management System backend built with FastAPI, SQLAlchemy ORM, and PostgreSQL.

## Features

- ✅ **Employee Management** - Create, read, update, and delete employee records
- ✅ **Attendance Tracking** - Mark and track employee attendance with date filters
- ✅ **RESTful API** - Complete REST API with proper HTTP status codes
- ✅ **Data Validation** - Pydantic schemas with comprehensive field validation
- ✅ **Error Handling** - Structured error responses with meaningful messages
- ✅ **CORS Support** - Cross-Origin Resource Sharing enabled for frontend integration
- ✅ **Database Relationships** - SQLAlchemy ORM with cascade deletes
- ✅ **UUID Primary Keys** - Secure, database-agnostic identifier generation

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0.23
- **Validation**: Pydantic 2.5.0
- **Database**: PostgreSQL
- **Database Driver**: psycopg2-binary 2.9.9
- **Server**: Uvicorn 0.24.0
- **Python Version**: 3.8+

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Settings and configuration
│   ├── database/
│   │   ├── __init__.py
│   │   └── session.py          # Database session management
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py           # SQLAlchemy ORM models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic validation schemas
│   └── routes/
│       ├── __init__.py
│       ├── employees.py        # Employee endpoints
│       └── attendance.py       # Attendance endpoints
├── .env.example                # Environment variable template
├── .gitignore
├── requirements.txt            # Python dependencies
└── README.md
```

## Installation

### 1. Clone the repository
```bash
cd backend
```

### 2. Create a virtual environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` and set your PostgreSQL connection details:
```env
DATABASE_URL=postgresql://user:password@localhost/hrms_lite_db
```

### 5. Initialize the database (optional - Alembic migrations not included in lite version)
```bash
# The database will be created automatically on first run
# Tables will be created when the app starts
```

## Running the Application

### Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
```

The API will be available at `http://localhost:3001`

### Production Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 3001
```

### API Documentation
- **Swagger UI**: `http://localhost:3001/docs`
- **ReDoc**: `http://localhost:3001/redoc`

## API Endpoints

### Base URL
```
http://localhost:3001/api
```

### Employee Endpoints

#### Create Employee
```http
POST /employees
Content-Type: application/json

{
  "employee_id": "EMP001",
  "full_name": "John Doe",
  "email": "john@example.com",
  "department": "Engineering"
}

Response: 201 Created
{
  "success": true,
  "message": "Employee created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "employee_id": "EMP001",
    "full_name": "John Doe",
    "email": "john@example.com",
    "department": "Engineering",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
}
```

#### Get All Employees
```http
GET /employees

Response: 200 OK
{
  "success": true,
  "message": "Employees retrieved successfully",
  "data": [...],
  "total": 5
}
```

#### Get Employee by ID
```http
GET /employees/{id}

Response: 200 OK or 404 Not Found
```

#### Update Employee
```http
PUT /employees/{id}
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "department": "HR"
}

Response: 200 OK or 404 Not Found
```

#### Delete Employee
```http
DELETE /employees/{id}

Response: 200 OK or 404 Not Found
```

### Attendance Endpoints

#### Mark Attendance
```http
POST /attendance
Content-Type: application/json

{
  "employee_id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2024-01-15",
  "status": "Present"
}

Response: 201 Created or 200 OK (if updating existing)
```

#### Get All Attendance Records
```http
GET /attendance?date=2024-01-15

Response: 200 OK
{
  "success": true,
  "message": "Attendance records retrieved successfully",
  "data": [...],
  "total": 20
}
```

#### Get Attendance by Employee
```http
GET /attendance/employee/{employee_id}?month=2024-01

Response: 200 OK
```

#### Delete Attendance Record
```http
DELETE /attendance/{id}

Response: 200 OK or 404 Not Found
```

## Database Schema

### Employees Table
```sql
CREATE TABLE employees (
  id UUID PRIMARY KEY,
  employee_id VARCHAR(50) UNIQUE NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  department VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employee_id ON employees(employee_id);
CREATE INDEX idx_email ON employees(email);
```

### Attendance Table
```sql
CREATE TABLE attendance (
  id UUID PRIMARY KEY,
  employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  status VARCHAR(20) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(employee_id, date)
);

CREATE INDEX idx_employee_attendance ON attendance(employee_id);
CREATE INDEX idx_date ON attendance(date);
```

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

### Common Error Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Validation error
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate resource (e.g., duplicate employee_id)
- `500 Internal Server Error` - Server error

## Validation Rules

### Employee Creation
- `employee_id`: Required, unique, alphanumeric
- `full_name`: Required, 1-255 characters
- `email`: Required, valid email format, unique
- `department`: Required, one of: HR, Engineering, Sales, Marketing, Finance, Operations

### Attendance Marking
- `employee_id`: Required UUID of existing employee
- `date`: Required, format YYYY-MM-DD
- `status`: Required, either "Present" or "Absent"
- Unique constraint: Only one attendance record per employee per day

## Development

### Running Tests (add with pytest)
```bash
pytest
```

### Code Style (add with black)
```bash
black app/
```

### Linting (add with flake8)
```bash
flake8 app/
```

## Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:3001
```

### Using Docker
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3001"]
```

Build and run:
```bash
docker build -t hrms-lite-backend .
docker run -p 3001:3001 --env-file .env hrms-lite-backend
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/hrms_lite_db

# Server Configuration
DEBUG=False
```

## License

MIT

## Support

For issues or questions, please create an issue in the repository.

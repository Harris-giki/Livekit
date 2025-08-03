from typing import Annotated
from pydantic import Field
from livekit.agents.llm import function_tool
from livekit.agents.voice import RunContext
from models import UserData, StudentDatabase
from config import logger

# Type alias for better readability
RunContext_T = RunContext[UserData]

# Initialize database
db = StudentDatabase()


@function_tool()
async def get_student_info(
    identifier: Annotated[str, Field(description="Student ID or student name to search for")],
    context: RunContext_T,
) -> str:
    """Retrieve student information by ID or name.
    Only returns information for students that exist in the database."""
    
    identifier = identifier.strip()
    student = None
    
    # Try to find by ID first, then by name
    student = db.get_student_by_id(identifier)
    if not student:
        student = db.get_student_by_name(identifier)
    
    if student:
        logger.info(f"Retrieved student info for: {identifier}")
        return (
            f"Student Information:\n"
            f"ID: {student['id']}\n"
            f"Name: {student['name']}\n"
            f"Major: {student['major']}\n"
            f"Year: {student['year']}\n"
            f"CGPA: {student['cgpa']}"
        )
    else:
        logger.info(f"Student not found: {identifier}")
        return f"Sorry, I couldn't find any student with ID or name '{identifier}' in our database."


@function_tool()
async def add_new_student(
    student_id: Annotated[str, Field(description="Student ID (required)")],
    name: Annotated[str, Field(description="Student full name (required)")],
    major: Annotated[str, Field(description="Student major/program (required)")],
    year: Annotated[int, Field(description="Admission year (required)")],
    cgpa: Annotated[float, Field(description="Current CGPA (required)", ge=0.0, le=4.0)],
    context: RunContext_T,
) -> str:
    """Add a new student to the database.
    All fields are required: ID, name, major, year, and CGPA."""
    
    # Clean the inputs
    student_id = student_id.strip()
    name = name.strip().title()
    major = major.strip().upper()
    
    # Validate CGPA range
    if not (0.0 <= cgpa <= 4.0):
        return "CGPA must be between 0.0 and 4.0. Please provide a valid CGPA."
    
    # Add to database
    success = db.add_student(student_id, name, major, year, cgpa)
    
    if success:
        logger.info(f"Added new student: {student_id} - {name}")
        return (
            f"Successfully added new student:\n"
            f"ID: {student_id}\n"
            f"Name: {name}\n"
            f"Major: {major}\n"
            f"Year: {year}\n"
            f"CGPA: {cgpa}"
        )
    else:
        return f"Failed to add student. Student ID '{student_id}' may already exist in the database."


@function_tool()
async def list_all_students(context: RunContext_T) -> str:
    """Get a list of all students in the database."""
    
    students = db.get_all_students()
    
    if not students:
        return "No students found in the database."
    
    logger.info(f"Retrieved list of {len(students)} students")
    
    # Create a formatted list
    student_list = [f"Here are all students in the database ({len(students)} total):"]
    
    for student in students:
        student_list.append(
            f"• {student['name']} (ID: {student['id']}) - {student['major']}, Year {student['year']}, CGPA: {student['cgpa']}"
        )
    
    return "\n".join(student_list)
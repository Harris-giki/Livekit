import os
from typing import Annotated
from pydantic import Field
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, RunContext
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

# MongoDB connection
client = None
database = None

async def get_mongodb_connection():
    """Get MongoDB connection"""
    global client, database
    
    if client is None:
        # Get connection string from environment variable
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        database_name = os.getenv('MONGODB_DATABASE_NAME', 'medical_db')
        
        if not connection_string:
            raise ValueError("Missing MONGODB_CONNECTION_STRING environment variable")
        
        # Add database name to connection string if not already included
        if f"/{database_name}" not in connection_string:
            connection_string = connection_string.rstrip('/') + f"/{database_name}?retryWrites=true&w=majority"
        
        client = AsyncIOMotorClient(connection_string)
        database = client[database_name]
        
        # Test connection
        await client.admin.command('ping')
    
    return database

@function_tool()
async def patient_lookup(
    patient_id: Annotated[str, Field(description="The patient's unique ID number")],
    context: RunContext,
) -> str:
    """Call this tool ONLY when the user provides their patient ID to retrieve their medical reports, test results, and prescription information. You MUST ask for the patient ID first before calling this tool."""
    
    try:
        # Let user know we're processing
        await context.session.generate_reply(
            instructions="Tell the user that you are retrieving their medical information from the database. This may take a moment."
        )
        
        # Get MongoDB connection
        db = await get_mongodb_connection()
        
        # Find patient - try both string and int patient_id
        patient = await db.patient_data.find_one({"patient_id": patient_id})
        if not patient:
            # Try with integer patient_id
            try:
                patient = await db.patient_data.find_one({"patient_id": int(patient_id)})
            except ValueError:
                pass
        
        if not patient:
            return f"No patient found with ID: {patient_id}. Please verify your patient ID and try again."
        
        # Format response based on your actual data structure
        response = f"**Patient Information for {patient.get('full_name', 'Unknown')}:**\n"
        response += f"Patient ID: {patient.get('patient_id')}\n"
        response += f"Date of Birth: {patient.get('date_of_birth', 'N/A')}\n"
        
        # Test Report
        if patient.get('test_report'):
            response += f"\n**Latest Test Report:**\n{patient.get('test_report')}\n"
        
        # Doctor's Prescription
        if patient.get('doctors_prescription'):
            prescription = patient.get('doctors_prescription')
            response += f"\n**Current Prescriptions:**\n"
            
            if prescription.get('medications'):
                for i, med in enumerate(prescription['medications'], 1):
                    response += f"{i}. **{med.get('medicine_name', 'Unknown')}**\n"
                    response += f"   - Dosage: {med.get('dosage', 'N/A')}\n"
                    response += f"   - Frequency: {med.get('frequency', 'N/A')}\n"
                    response += f"   - Duration: {med.get('duration', 'N/A')}\n\n"
            
            if prescription.get('special_instructions'):
                response += f"**Special Instructions:**\n{prescription.get('special_instructions')}\n"
            
            if prescription.get('lifestyle_recommendations'):
                response += f"\n**Lifestyle Recommendations:**\n{prescription.get('lifestyle_recommendations')}\n"
        
        return response
        
    except Exception as e:
        return f"Sorry, I encountered an error while retrieving your medical information: {str(e)}. Please try again later."


@function_tool()
async def book_appointment(
    context: RunContext,
    patient_full_name: Annotated[str, Field(description="The patient's full name")],
    patient_id: Annotated[str, Field(description="The patient's ID number")],
    doctor_specialty: Annotated[str, Field(description="The type of doctor to meet (e.g., cardiologist, neurologist, general physician)")],
    appointment_date: Annotated[str, Field(description="The date for the appointment (format: YYYY-MM-DD)")],
    appointment_time: Annotated[str, Field(description="The time for the appointment (format: HH:MM)")],
) -> str:
    """
    Book an appointment with a doctor for a patient.
    
    Args:
        patient_full_name: The patient's full name
        patient_id: The patient's ID number
        doctor_specialty: The type of doctor to meet (e.g., cardiologist, neurologist, general physician)
        appointment_date: The date for the appointment (format: YYYY-MM-DD)
        appointment_time: The time for the appointment (format: HH:MM)
    """
    
    try:
        # Let user know we're processing
        await context.session.generate_reply(
            instructions="Tell the user that you are booking their appointment. This may take a moment."
        )
        
        # Get MongoDB connection
        db = await get_mongodb_connection()
        
        # Create appointment document
        appointment_data = {
            "patient_full_name": patient_full_name,
            "patient_id": patient_id,
            "doctor_specialty": doctor_specialty,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "status": "scheduled",
            "created_at": context.session.start_time.isoformat() if hasattr(context.session, 'start_time') else None
        }
        
        # Insert appointment into database
        result = await db.appointments.insert_one(appointment_data)
        
        if result.inserted_id:
            return f"✅ Appointment booked successfully!\n\n**Appointment Details:**\n- Patient: {patient_full_name} (ID: {patient_id})\n- Doctor: {doctor_specialty}\n- Date: {appointment_date}\n- Time: {appointment_time}\n- Status: Scheduled\n\nYour appointment has been confirmed. Please arrive 15 minutes early."
        else:
            return "❌ Failed to book appointment. Please try again later."
        
    except Exception as e:
        return f"Sorry, I encountered an error while booking your appointment: {str(e)}. Please try again later."

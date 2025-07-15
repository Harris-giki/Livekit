from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, RoomInputOptions, llm
from livekit.plugins import (
    groq,
    noise_cancellation,
    silero,  # For VAD
)
from prompts import INSTRUCTIONS, WELCOME_MESSAGE, LOOKUP_VIN_MESSAGE
from db_driver import DatabaseDriver
import enum
from typing import Annotated
import logging
import sqlite3
import asyncio
import re

load_dotenv()

# Set up logging
logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

# Initialize database
DB = DatabaseDriver()

class CarDetails(enum.Enum):
    VIN = "vin"
    Make = "make"
    Model = "model"
    Year = "year"

class CarFunctions:
    def __init__(self):
        # Car details storage
        self._car_details = {
            CarDetails.VIN: "",
            CarDetails.Make: "",
            CarDetails.Model: "",
            CarDetails.Year: ""
        }
        # Temporary storage for car creation process
        self._temp_car_info = {}
    
    def get_car_str(self):
        if not self.has_car():
            return "No car information available"
        
        car_str = ""
        for key, value in self._car_details.items():
            car_str += f"{key.value}: {value}\n"
        return car_str
    
    def lookup_car(self, vin: str):
        """Look up a car by VIN in the database"""
        logger.info("lookup car - vin: %s", vin)
        
        result = DB.get_car_by_vin(vin)
        if result is None:
            logger.info("Car not found in database for VIN: %s", vin)
            return None
        
        self._car_details = {
            CarDetails.VIN: result.vin,
            CarDetails.Make: result.make,
            CarDetails.Model: result.model,
            CarDetails.Year: result.year
        }
        
        logger.info("Car found and loaded: %s", self.get_car_str())
        return f"Found your vehicle: {result.year} {result.make} {result.model} (VIN: {result.vin})"
    
    def store_temp_car_info(self, year=None, make=None, model=None):
        """Store temporary car information during creation process"""
        if year:
            self._temp_car_info['year'] = year
        if make:
            self._temp_car_info['make'] = make
        if model:
            self._temp_car_info['model'] = model
    
    def can_create_car(self):
        """Check if we have enough info to create a car"""
        required_fields = ['vin', 'year', 'make', 'model']
        return all(field in self._temp_car_info for field in required_fields)
    
    def create_car_from_temp(self):
        """Create car using stored temporary information"""
        if not self.can_create_car():
            return "Missing information. I need VIN, year, make, and model to create your profile."
        
        return self.create_car(
            self._temp_car_info['vin'],
            self._temp_car_info['make'],
            self._temp_car_info['model'],
            self._temp_car_info['year']
        )
    
    def get_car_details(self):
        logger.info("get car details")
        if not self.has_car():
            return "No car information is currently loaded. Please provide your VIN first."
        return f"Your current vehicle details:\n{self.get_car_str()}"
    
    def create_car(self, vin: str, make: str, model: str, year: int):
        logger.info("create car - vin: %s, make: %s, model: %s, year: %s", vin, make, model, year)
        
        try:
            # Check if car already exists
            existing_car = DB.get_car_by_vin(vin)
            if existing_car:
                # Load existing car instead of creating duplicate
                self._car_details = {
                    CarDetails.VIN: existing_car.vin,
                    CarDetails.Make: existing_car.make,
                    CarDetails.Model: existing_car.model,
                    CarDetails.Year: existing_car.year
                }
                return f"Car profile already exists! Loaded your vehicle: {existing_car.year} {existing_car.make} {existing_car.model} (VIN: {existing_car.vin})"
            
            # Create new car - your DB driver always returns a Car object
            result = DB.create_car(vin, make, model, year)
            
            self._car_details = {
                CarDetails.VIN: result.vin,
                CarDetails.Make: result.make,
                CarDetails.Model: result.model,
                CarDetails.Year: result.year
            }
            
            logger.info("Car profile created successfully: %s", self.get_car_str())
            return f"Car profile created successfully! Your vehicle: {result.year} {result.make} {result.model} (VIN: {result.vin})"
        
        except sqlite3.IntegrityError as e:
            logger.error("Duplicate VIN error: %s", str(e))
            return f"A car with VIN {vin} already exists in our system. Let me look it up for you."
        except Exception as e:
            logger.error("Error creating car: %s", str(e))
            return f"Error creating car profile: {str(e)}"
    
    def has_car(self):
        return self._car_details[CarDetails.VIN] != ""
    
    def extract_vin_from_text(self, text: str):
        """Extract VIN from user text - VINs are typically 17 alphanumeric characters"""
        # Remove spaces and common separators
        clean_text = re.sub(r'[^A-Za-z0-9]', '', text.upper())
        
        # Look for 17 character sequences
        vin_pattern = r'[A-HJ-NPR-Z0-9]{17}'
        matches = re.findall(vin_pattern, clean_text)
        
        return matches[0] if matches else None

class Assistant(Agent):
    def __init__(self, car_functions: CarFunctions) -> None:
        super().__init__(instructions=INSTRUCTIONS)
        self.car_functions = car_functions

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()
    
    # Create the car functions instance
    car_functions = CarFunctions()
    
    # Create the assistant instance
    assistant = Assistant(car_functions)
    
    # Create session with Groq components
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=groq.STT(
            model="whisper-large-v3-turbo",
            language="en",
        ),
        llm=groq.LLM(
            model="llama3-8b-8192"
        ),
        tts=groq.TTS(
            model="playai-tts",
            voice="Arista-PlayAI",
        ),
    )
    
    await session.start(
        room=ctx.room,
        agent=assistant,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    # Send welcome message
    await session.generate_reply(
        instructions=f"Say this welcome message: {WELCOME_MESSAGE}"
    )
    
    # Set up event handlers
    def on_user_speech_committed(msg: llm.ChatMessage):
        if isinstance(msg.content, list):
            msg.content = "\n".join("[image]" if isinstance(x, llm.ChatImage) else x for x in msg.content)
        
        # Create task for async processing
        asyncio.create_task(process_user_message(msg.content))
    
    session.on("user_speech_committed", on_user_speech_committed)
    
    def parse_car_details(text: str):
        """Parse car details from natural language - strict parsing with no assumptions"""
        text_lower = text.lower()
        car_info = {}
        
        # Extract year (4 digits) - must be between 1900 and current year
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            year = int(year_match.group())
            current_year = 2024  # You might want to make this dynamic
            if 1900 <= year <= current_year:
                car_info['year'] = year
        
        # Common car makes - must match exactly
        makes = {
            'toyota': 'Toyota',
            'honda': 'Honda',
            'ford': 'Ford',
            'chevrolet': 'Chevrolet',
            'chevy': 'Chevrolet',
            'bmw': 'BMW',
            'mercedes': 'Mercedes',
            'audi': 'Audi',
            'nissan': 'Nissan',
            'hyundai': 'Hyundai',
            'kia': 'Kia',
            'mazda': 'Mazda',
            'subaru': 'Subaru',
            'volkswagen': 'Volkswagen',
            'vw': 'Volkswagen'
        }
        
        # Look for exact make matches
        for make_key, make_value in makes.items():
            if f" {make_key} " in f" {text_lower} " or text_lower.startswith(make_key + " ") or text_lower.endswith(" " + make_key):
                car_info['make'] = make_value
                break
        
        # Try to extract model - must be after the make
        if car_info.get('make'):
            words = text_lower.split()
            make_index = -1
            for i, word in enumerate(words):
                if car_info['make'].lower() in word:
                    make_index = i
                    break
            
            if make_index >= 0 and make_index + 1 < len(words):
                # Get the next word as potential model
                potential_model = words[make_index + 1]
                # Only accept if it's a reasonable length and not a common word
                if 2 <= len(potential_model) <= 20 and potential_model not in ['a', 'the', 'is', 'was', 'and', 'or']:
                    car_info['model'] = potential_model.title()
        
        return car_info

    async def process_user_message(content: str):
        """Process user message and handle function calls based on prompts"""
        content_lower = content.lower()
        
        # If no car is loaded, follow VIN lookup logic
        if not car_functions.has_car():
            # Try to extract VIN from user input
            potential_vin = car_functions.extract_vin_from_text(content)
            
            if potential_vin:
                # Attempt VIN lookup in database
                lookup_result = car_functions.lookup_car(potential_vin)
                
                if lookup_result is not None:  # Car found in database
                    await session.generate_reply(
                        instructions=f"Great! {lookup_result}. How can I help you with your vehicle today?"
                    )
                else:  # Car not found in database
                    # Store VIN for potential car creation
                    car_functions._temp_car_info['vin'] = potential_vin
                    await session.generate_reply(
                        instructions=f"I couldn't find a profile for VIN {potential_vin} in our database. To create a new profile, I'll need the make, model, and year of your vehicle. Please provide these details. For example, say 'It's a 2020 Honda Civic'"
                    )
                return
            
            # Check if user is providing car details for creation (after VIN not found)
            elif 'vin' in car_functions._temp_car_info:
                # Try to parse car details from natural language
                car_info = parse_car_details(content)
                
                # Only proceed if we have all required information
                if car_info.get('year') and car_info.get('make') and car_info.get('model'):
                    # Store the car details temporarily
                    car_functions.store_temp_car_info(
                        year=car_info['year'],
                        make=car_info['make'],
                        model=car_info['model']
                    )
                    
                    # Create the car profile in database
                    if car_functions.can_create_car():
                        result = car_functions.create_car_from_temp()
                        await session.generate_reply(
                            instructions=result
                        )
                    else:
                        await session.generate_reply(
                            instructions="I need more details to create your profile. Please provide the year, make, and model of your vehicle. For example: 'It's a 2020 Honda Civic'"
                        )
                else:
                    # If we're missing any information, ask for it specifically
                    missing_info = []
                    if not car_info.get('year'):
                        missing_info.append("year")
                    if not car_info.get('make'):
                        missing_info.append("make")
                    if not car_info.get('model'):
                        missing_info.append("model")
                    
                    await session.generate_reply(
                        instructions=f"I need more details to create your profile. Please provide the {', '.join(missing_info)} of your vehicle. For example: 'It's a 2020 Honda Civic'"
                    )
            else:
                # No VIN detected, ask for VIN
                await session.generate_reply(
                    instructions="Please provide your vehicle's VIN number so I can look up your profile. If you don't have a profile, I'll help you create one."
                )
        
        else:
            # Car is loaded, handle queries with car context
            if "car details" in content_lower or "vehicle details" in content_lower or "show details" in content_lower:
                details = car_functions.get_car_details()
                await session.generate_reply(
                    instructions=f"Here are your vehicle details: {details}. Is there anything specific you'd like to know about your vehicle?"
                )
            
            elif any(word in content_lower for word in ["service", "appointment", "maintenance", "repair", "oil change", "tire", "brake"]):
                vehicle_info = f"{car_functions._car_details[CarDetails.Year]} {car_functions._car_details[CarDetails.Make]} {car_functions._car_details[CarDetails.Model]}"
                await session.generate_reply(
                    instructions=f"I can help you with service for your {vehicle_info}. Let me connect you with our service department. What type of service do you need? We offer oil changes, tire services, brake repairs, and general maintenance."
                )
            
            elif any(word in content_lower for word in ["parts", "part"]):
                vehicle_info = f"{car_functions._car_details[CarDetails.Year]} {car_functions._car_details[CarDetails.Make]} {car_functions._car_details[CarDetails.Model]}"
                await session.generate_reply(
                    instructions=f"I can help you find parts for your {vehicle_info}. Let me connect you with our parts department. What specific part do you need?"
                )
            
            elif any(word in content_lower for word in ["warranty", "coverage"]):
                vehicle_info = f"{car_functions._car_details[CarDetails.Year]} {car_functions._car_details[CarDetails.Make]} {car_functions._car_details[CarDetails.Model]}"
                await session.generate_reply(
                    instructions=f"I can help you with warranty information for your {vehicle_info}. Let me check your coverage details or connect you with our warranty department."
                )
            
            else:
                # General conversation with car context
                vehicle_info = f"{car_functions._car_details[CarDetails.Year]} {car_functions._car_details[CarDetails.Make]} {car_functions._car_details[CarDetails.Model]}"
                await session.generate_reply(
                    instructions=f"User said: {content}. Current vehicle: {vehicle_info}. Respond helpfully as Alexa, the call center manager, and direct them to the appropriate department if needed."
                )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
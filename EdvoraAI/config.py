import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("student-voice-agent")
logger.setLevel(logging.INFO)

# Database configuration
DATABASE_PATH = "students.db"
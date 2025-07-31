import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("restaurant-example")
logger.setLevel(logging.INFO)

# Voice configurations for different agents
VOICES = {
    "greeter": "794f9389-aac1-45b6-b726-9d9369183238",
    "reservation": "156fb8d2-335b-4950-9cb3-a2d33befec77", 
    "takeaway": "6f84f4b8-58a2-430c-8c79-688dad597532",
    "checkout": "39b376fc-488e-4d0c-8b37-e00b72059fdd",
}

# Restaurant menu
MENU = "Pizza: $10, Salad: $5, Ice Cream: $3, Coffee: $2"
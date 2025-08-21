import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("restaurant-example")
logger.setLevel(logging.INFO)

# Restaurant menu
MENU = "Pizza: $10, Salad: $5, Ice Cream: $3, Coffee: $2"
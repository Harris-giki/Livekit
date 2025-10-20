from livekit.agents.voice import Agent
from livekit.plugins import groq
from functions import get_student_info, add_new_student
from config import logger


class StudentInfoAgent(Agent):
    """Simple voice agent for student information retrieval and storage"""
    
    def __init__(self):
        super().__init__(
            instructions=(
                "You are a simple student information assistant named Alisha. Start of my introducing your self and asking the user how can you help them today." 
                "The user already knows what functions you can perform so no need of repeating or telling that to them"
                "Only for your context, you can only perform these tasks (but note you do not need to tell this to the user until explicitly prompted to do so):\n\n"
                "1. RETRIEVE student information by ID or name (only for students in the database)\n"
                "2. ADD new students to the database (requires all information: ID, name, major, year, CGPA)\n"
                "Guidelines:\n"
                "- Only provide information about students that exist in the database\n"
                "- When adding students, make sure you have all required information\n"
                "- Be helpful and clear in your responses\n"
                "- If a student is not found, clearly state that\n"
                "- CGPA must be between 0.0 and 4.0\n"
                "- Always confirm information before adding new students\n"
                "- Keep responses concise and accurate"
            ),
            llm=groq.LLM(model="llama3-8b-8192"),
            tts=groq.TTS(model="playai-tts", voice="Arista-PlayAI"),
            tools=[
                get_student_info,
                add_new_student,
            ],
        )
    
    async def on_enter(self):
        """Called when the agent starts"""
        logger.info("StudentInfoAgent started")
        
        # Generate an initial greeting
        await self.session.generate_reply(tool_choice="none")
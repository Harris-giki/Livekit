"""
Centralized imports and mappings for all LiveKit providers
Static imports required by LiveKit framework (must be on main thread)
"""

# Import all available LiveKit providers at once
from livekit.plugins import (
    upliftai,
     openai, 
    # cartesia, 
    deepgram, 
    groq,
    elevenlabs
)


class ProviderMappings:
    """Centralized mapping of provider names to their corresponding plugin modules"""

    @classmethod
    def get_provider(cls, provider_name: str):
        """Get provider module by name"""
        # Mapping for currently imported providers
        provider_map = {
            # Currently imported providers
            'openai': openai,
            'groq': groq,
            # 'cartesia': cartesia,
            'deepgram': deepgram,
            'elevenlabs': elevenlabs,
            'upliftai': upliftai,
            # Special OpenAI providers
            'with_cerebras_openai': openai,
            'with_deepseek_openai': openai,
            'with_fireworks_openai': openai,
            'with_letta_openai': openai,
            'with_ollama_openai': openai,
            'with_azure_openai': openai,
            'with_perplexity_openai': openai,
            'with_telnyx_openai': openai,
            'with_together_openai': openai,
            'with_x_ai_openai': openai,
        }
        return provider_map.get(provider_name.lower())

    @classmethod
    def get_openai_provider(cls):
        """Get OpenAI provider for special method calls"""
        return openai
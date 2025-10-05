default_bp = {
    "name": "Radiance",
    "voice": {
        "model": "eleven_turbo_v2_5",
        "voice_id": "Fahco4VZzobUeiPqni1S",
        "provider": "elevenlabs"
    },
    "model": {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "Your name is Radiance, a human-like AI character for medical assistance developed by Muhammad Haris who speaks and responds in Urdu Language..."
            }
        ],
        "provider": "openai"
    },
    "firstMessage": "(Speak in Urdu) Hi!, I'm Radiance, your AI medical assistant. How can I help you today?",
    "endCallMessage": "Goodbye.",
    "transcriber": {
        "language_code": "urd",
        "provider": "elevenlabs"
    },
    "backgroundSound": "off",
    "firstMessageMode": "assistant-speaks-first-with-model-generated-message",
    "backgroundDenoisingEnabled": True,
    "startSpeakingPlan": {
        "smartEndpointingPlan": {
            "provider": "livekit",
            "waitFunction": "150 + 300 * x"
        }
    },
    "tools": [
    {
        "type": "function",
        "function": {
            "name": "patient_lookup",
            "description": "Call this tool ONLY when the user provides their patient ID to retrieve their medical reports, test results, and prescription information. You MUST ask for the patient ID first before calling this tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "description": "Unique patient ID number (numeric value) provided by the patient",
                        "type": "string"
                    }
                },
                "required": ["patient_id"]
            }
        },
        "server": {
            "url": "http://localhost:5678/webhook/patient-lookup"
        }
    }
]
}

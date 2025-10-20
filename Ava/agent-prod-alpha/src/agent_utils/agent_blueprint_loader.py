import json
from livekit.agents import get_job_context

def load_agent_metadata(ctx=None):
    if ctx is None:
        ctx = get_job_context()

    from .default_agent import default_bp

    try:
        if ctx.job.metadata and ctx.job.metadata.strip():
            return json.loads(ctx.job.metadata)
        else:
            # If default_bp is already a dict, return it directly
            return default_bp if isinstance(default_bp, dict) else json.loads(default_bp)
    except json.JSONDecodeError:
        # If metadata is invalid JSON, return default_bp safely
        return default_bp if isinstance(default_bp, dict) else json.loads(default_bp)

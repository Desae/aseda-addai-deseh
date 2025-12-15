from .executor import execute_agentic_pipeline
from .memory import profile_store

def handle_message(user_input: str, session_id: str = "default"):
    """
    This is the root entrypoint an ADK Playground will call.
    """
    return execute_agentic_pipeline(user_input, session_id, profile_store)


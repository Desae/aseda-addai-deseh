import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# --- Gemini configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Create a .env file and add GEMINI_API_KEY=your_key_here."
    )

# Setting default model name if not provided
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash")

# --- Serper.dev configuration (for Google search) ---
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
if not SERPER_API_KEY:
    raise RuntimeError(
        "SERPER_API_KEY is not set. "
        "Create a .env file and add SERPER_API_KEY=your_key_here."
    )

SERPER_SEARCH_URL = "https://google.serper.dev/search"

# General app settings
APP_NAME = "GradPath"
MIN_PROGRAM_RESULTS = 5
MAX_PROGRAM_RESULTS = 10

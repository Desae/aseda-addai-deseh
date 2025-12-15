import json
from typing import Dict, Any

import google.generativeai as genai

from .config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from .memory import StudentProfile, InMemoryProfileStore

# Configure Gemini once
genai.configure(api_key=GEMINI_API_KEY)


PLANNER_SYSTEM_PROMPT = """
You are the GradPath Planner.

Your job:
1. Read the student's natural-language request.
2. Combine it with any existing profile data (GPA, tests, countries, funding, etc.).
3. Update the profile if new details are provided.
4. Produce a JSON "search plan" for finding grad programs.

You ALWAYS output VALID JSON, no extra text.
Structure:

{
  "high_level_goal": "...",
  "profile_updates": {
    "gpa": "... or null",
    "gre": "... or null",
    "ielts": "... or null",
    "toefl": "... or null",
    "field_of_study": "... or null",
    "degree_level": "... or null",
    "preferred_countries": "... or null",
    "preferred_cities": "... or null",
    "funding_needs": "... or null",
    "intake_term": "... or null",
    "budget_notes": "... or null",
    "extra_notes": "... or null"
  },
  "filters": {
    "field_of_study": "...",
    "degree_type": ["MSc", "PhD", ...],
    "countries_or_regions": ["United States", "Canada", ...],
    "cities_or_states": ["..."],
    "funding_priority": ["RA", "TA", "scholarship", ...],
    "budget_notes": "...",
    "target_intake_terms": ["Fall 2026"],
    "minimum_requirements": {
      "gpa": "approx or unknown",
      "tests": ["GRE optional", "IELTS >= 7.0", "unknown"]
    },
    "other_constraints": ["international friendly", "no GRE", ...]
  },
  "search_queries": [
    "MS Data Science fully funded USA",
    "MS Data Science funding Canada",
    "Data Science graduate program scholarships no GRE"
  ],
  "notes_for_search": "any extra hints for the search step"
}

IMPORTANT SEARCH QUERY RULES:
- Keep queries SIMPLE and natural (like how people actually search)
- DO NOT use too many quoted phrases together - this returns 0 results
- Use 1-2 quoted phrases MAX per query (e.g., "Data Science" OR "MS program")
- Avoid site: operators unless specifically needed
- Use natural language: "MS Data Science funding USA" NOT site:.edu "MS" "Data Science" "funding"
- Generate 5-7 different queries with different keyword combinations
- Focus on findable terms: program names, degree types, countries, funding types
- Each query should be distinct and target different aspects:
  * Query 1-2: General program pages (e.g., "PhD Machine Learning USA")
  * Query 3-4: Funding-specific (e.g., "Machine Learning PhD funding scholarships")
  * Query 5-6: Requirements/admissions (e.g., "PhD Machine Learning admission requirements")
  * Query 7: Specialty focus if applicable (e.g., "Machine Learning healthcare AI PhD")
- Vary the keyword order and combinations to catch different result sets

Examples of GOOD queries:
- "MS Data Science" fully funded scholarships
- Data Science graduate programs Canada funding
- MS Data Science no GRE required USA

Examples of BAD queries (too restrictive):
- site:.edu "MS Data Science" "full funding" "no GRE" "international students"
- "Master of Science" "Data Science" "RA" "TA" "GRE waiver"
"""


def build_planner_prompt(user_input: str, profile: StudentProfile) -> str:
    return f"""
SYSTEM:
{PLANNER_SYSTEM_PROMPT}

CURRENT PROFILE (JSON):
{json.dumps(profile.__dict__, indent=2)}

USER REQUEST:
{user_input}
"""


def plan_from_user_input(
    user_input: str,
    session_id: str,
    store: InMemoryProfileStore,
) -> Dict[str, Any]:
    """
    Call Gemini to create a search plan and update student profile memory.
    """
    profile = store.get_profile(session_id)
    prompt = build_planner_prompt(user_input, profile)

    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(prompt)
    
    text = response.text.strip() if response.text else ""

    # Check if response is empty
    if not text:
        raise ValueError("Gemini returned an empty response. This may be due to content filtering, rate limits, or quota issues.")

    # Extract JSON from markdown code blocks if present
    if text.startswith("```"):
        # Remove markdown code block markers
        lines = text.split("\n")
        # Skip first line (```json or similar) and last line (```)
        if len(lines) > 2:
            text = "\n".join(lines[1:-1])
        # Also handle case where language identifier is on same line as opening ```
        if text.startswith("json\n"):
            text = text[5:]
        text = text.strip()

    # Try to parse JSON with better error handling
    try:
        plan: Dict[str, Any] = json.loads(text)
    except json.JSONDecodeError as e:
        # Log the problematic JSON for debugging
        print(f"[ERROR] Failed to parse JSON from Gemini planner:")
        print(f"Error: {e}")
        print(f"Response text (first 500 chars): {text[:500]}")
        
        # Try to fix common JSON issues
        # Remove trailing commas before closing braces/brackets
        import re
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        try:
            plan: Dict[str, Any] = json.loads(text)
            print("[INFO] Successfully parsed JSON after cleanup")
        except json.JSONDecodeError as e2:
            # If still failing, return a basic plan
            print(f"[ERROR] Still failed after cleanup: {e2}")
            print("[INFO] Returning fallback plan")
            plan = {
                "high_level_goal": "Search for graduate programs",
                "profile_updates": {},
                "filters": {
                    "field_of_study": "unknown",
                    "degree_type": ["MS", "PhD"],
                    "countries_or_regions": ["United States", "Canada"],
                },
                "search_queries": [
                    f'site:.edu "MS" "graduate program" "{text[:50]}"',
                ],
                "notes_for_search": "Fallback search due to JSON parsing error"
            }

    # Apply profile_updates into memory
    updates = plan.get("profile_updates", {}) or {}
    print(f"[DEBUG] Applying profile updates: {updates}")
    store.update_profile(session_id, **updates)
    
    # Verify updates were applied
    updated_profile = store.as_dict(session_id)
    print(f"[DEBUG] Profile after updates: {json.dumps(updated_profile, indent=2)}")

    return plan

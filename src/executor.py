import json
from typing import Dict, Any, List

import google.generativeai as genai

from .config import (
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME,
    MIN_PROGRAM_RESULTS,
    MAX_PROGRAM_RESULTS,
)
from .memory import InMemoryProfileStore
from .tools.search import serper_program_search, extract_program_candidates

# Configure Gemini once
genai.configure(api_key=GEMINI_API_KEY)


QUERY_CLASSIFIER_PROMPT = """
You are a query classifier. Analyze the user's message and determine what type of query it is.

Types:
1. "deep_dive" - User wants more details about a specific university/program
   Examples: "Tell me more about Stanford", "What are the requirements for CMU's program?"
   
2. "compare" - User wants to compare multiple universities
   Examples: "Compare MIT and Stanford", "What's the difference between funding at CMU vs Berkeley?"
   
3. "new_search" - User wants to search for new programs or modify their search
   Examples: "I want programs in AI", "Show me PhD programs in Europe"

Output ONLY valid JSON:
{
  "query_type": "deep_dive" | "compare" | "new_search",
  "universities": ["university names mentioned"],
  "comparison_aspects": ["aspects to compare like funding, requirements, location"],
  "notes": "any additional context"
}
"""


DEEP_DIVE_PROMPT = """
You are GradPath, an expert graduate program advisor providing comprehensive, in-depth analysis.

The user has asked about: {university_query}

Using ALL the search results provided below, create an EXTENSIVE, DETAILED report covering:

## 1. 📋 Program Overview
- Full program name and degree type
- Department/School/College affiliation
- Program duration and structure
- Core curriculum and specializations
- Research focus areas
- Faculty expertise and notable researchers

## 2. 🎓 Admission Requirements
- Minimum GPA requirements (overall and major-specific)
- Required test scores (GRE, GMAT, TOEFL, IELTS) with minimum scores
- Required prerequisites and recommended background
- Application materials (transcripts, letters of recommendation, statement of purpose, CV/resume, writing samples)
- Portfolio or additional requirements if applicable
- International student requirements

## 3. 💰 Funding & Financial Support
- Full tuition coverage details
- Research Assistantships (RA): availability, stipend amounts, responsibilities
- Teaching Assistantships (TA): availability, stipend amounts, responsibilities
- Fellowships: named fellowships, eligibility, amounts
- Scholarships: internal and external opportunities
- Cost of living estimates and stipend adequacy
- Health insurance coverage
- Additional funding sources (conference travel, research grants)

## 4. 📅 Application Process & Deadlines
- Application deadlines (Fall, Spring, Summer intakes)
- Application fee and fee waiver availability
- Application portal and submission process
- Interview process (if applicable)
- Decision timeline
- Acceptance rate or competitiveness level

## 5. 🔬 Research Opportunities
- Active research labs and centers
- Key research areas and ongoing projects
- Interdisciplinary opportunities
- Industry partnerships and collaborations
- Access to specialized equipment/facilities
- Publication expectations

## 6. 🌟 Unique Features & Distinguishing Factors
- Program rankings and reputation
- Notable alumni and career outcomes
- Industry connections and internship opportunities
- International collaboration and exchange programs
- Professional development and career support
- Unique aspects that set this program apart
- Student organizations and networking opportunities

## 7. 📍 Campus & Location Information
- Campus facilities and resources
- Location advantages (proximity to industry, research centers, hospitals)
- Quality of life and student community
- Housing options for graduate students

## 8. 📚 References & Official Links
- Official program website
- Application portal
- Department contact information
- Virtual tour or information session links
- Student testimonials or program blogs (if available)

CRITICAL INSTRUCTIONS:
- Be THOROUGH and DETAILED - this is a comprehensive research report
- Use ALL available information from search results
- Include SPECIFIC numbers, dates, and amounts whenever available
- If precise information isn't available, provide ranges or say "Check program website for exact details: [Link](URL)"
- Speak directly to the user using "you" and "your"
- Format ALL links as [Text](URL)
- If a section has no information, say "Information not found in search results. Please visit [Program Website](URL) for details."
- Aim for a comprehensive 500-800 word report minimum
- Be honest about gaps in information

SEARCH RESULTS:
{search_results}

Now provide the extensive, well-structured report above. Make it thorough and actionable!
"""


COMPARISON_PROMPT = """
You are GradPath, helping someone compare multiple university programs.

The user wants to compare: {universities}
Focusing on: {aspects}

Using the search results below, create a comparison table and analysis directly for them.

Format:
1. **Comparison Table** - Use markdown table with columns for each aspect
2. **Key Differences** - Bullet points highlighting major differences for you
3. **My Recommendations** - Which might be better based on your profile and goals
4. **References** - Where you can learn more about each program

IMPORTANT:
- Speak directly to the user using "you" and "your"
- Be conversational: "You might prefer X if..." instead of "Students might prefer..."
- ALWAYS include website links in the table (add a "Link" column)
- Format links as: [Link](URL) - use standard markdown links, NOT HTML
- DO NOT use HTML tags like <br> in the output - use proper markdown formatting
- For line breaks in table cells, just use normal text flow or separate rows
- Add a **References** section at the end with all relevant links organized by university

SEARCH RESULTS:
{search_results}

Remember to include website links in the table AND a **References** section at the end!
"""


FOLLOWUP_GENERATOR_PROMPT = """
You are GradPath's follow-up question generator. After providing search results, suggest 2-3 intelligent, contextual follow-up questions to continue the conversation naturally.

CONTEXT:
Student Profile: {profile}
Query Type: {query_type}
Results Provided: {results_summary}

Generate 2-3 follow-up questions that:
1. Help narrow down or refine their search
2. Address common concerns (funding, deadlines, requirements)
3. Encourage deeper exploration of specific programs
4. Are personalized to their profile and results

Output ONLY valid JSON:
{{
  "follow_up_questions": [
    "Question 1 addressing a specific gap or opportunity",
    "Question 2 encouraging deeper exploration",
    "Question 3 about next steps or priorities"
  ],
  "reasoning": "Brief explanation of why these questions are relevant"
}}

RULES:
- Questions should be conversational and natural
- Frame as helpful suggestions: "Would you like to...", "Should I...", "Are you interested in..."
- Make them specific to the programs found and their profile
- Avoid generic questions - personalize based on context
- Each question should open a different avenue of exploration

Examples of GOOD follow-up questions:
- "Would you like me to compare the funding opportunities at Stanford vs MIT?"
- "Should I look for programs with later deadlines since most close in January?"
- "Are you interested in learning more about the AI research labs at CMU?"
- "Would you like to explore programs that don't require the GRE?"

Examples of BAD follow-up questions (too generic):
- "Do you have any questions?"
- "Would you like more information?"
- "Is there anything else?"
"""


COORDINATOR_SYSTEM_PROMPT = """
You are the GradPath Coordinator. Your job is to decide whether you have enough information to search for programs, or if you need to ask more questions.

CRITICAL: Look at BOTH the profile AND the user's current message. Information already provided should NEVER be asked for again.

STEP 1: Extract information from user's current message:
- Field of study: Look for mentions like "Data Science", "Computer Science", "Engineering", "MBA", etc.
- Degree level: Look for "Masters", "Master's", "MS", "MSc", "PhD", "Doctorate"
- Location: Look for countries, states, regions, continents
- GPA: Look for numbers like "3.4 GPA", "3.8", "4.0 GPA"
- Funding: Look for "affordable", "funded", "scholarship", "financial aid", "funding"
- Test scores: Look for "GRE", "GMAT", "TOEFL", "IELTS"

STEP 2: Combine with existing profile to determine what's ACTUALLY missing.

STEP 3: Determine if you can proceed:
MINIMUM REQUIRED INFO:
- Field of study (either from profile OR current message)
- Degree level (either from profile OR current message)
- Location preference (either from profile OR current message)

NICE TO HAVE (ask if truly missing, but not blockers):
- Funding needs
- GPA

Output ONLY valid JSON in this format:
{
  "needs_more_info": true or false,
  "missing_info": ["list", "of", "ACTUALLY missing", "details"],
  "questions_to_ask": "A friendly message asking ONLY for truly missing information. NEVER ask for info already in profile or current message.",
  "ready_to_search": true or false,
  "extracted_info": {
    "field": "ACTUAL field from current message, or null if not mentioned",
    "degree_level": "ACTUAL degree level from current message, or null if not mentioned",
    "location": "ACTUAL location from current message, or null if not mentioned",
    "gpa": "ACTUAL GPA from current message, or null if not mentioned",
    "funding_preference": "ACTUAL funding info from current message, or null if not mentioned",
    "other_notes": "any other relevant details"
  }
}

IMPORTANT for extracted_info:
- Put the ACTUAL VALUE if you found it in the current message (e.g., "Master's", "Data Science", "3.4")
- Put null if it's NOT in the current message (even if it's in the profile)
- NEVER put placeholder text like "already in profile" - use null instead
- This helps us save NEW information from the current message to memory

Rules:
- If profile already has field_of_study, DON'T ask about field again
- If profile already has degree_level, DON'T ask about degree level again
- If profile already has preferred_countries, DON'T ask about location again
- If user just provided info in current message, DON'T ask for it again
- If you have field + degree_level + location (from EITHER source), you CAN search
- Only ask about funding/GPA as optional follow-up questions AFTER confirming required fields
- Use 2nd person language ("you", "your")
"""


WRITER_SYSTEM_PROMPT = f"""
You are GradPath, a friendly advisor helping someone find graduate programs.

You receive:
- Their profile (JSON) - their background and preferences
- A search plan (JSON) with filters and search_queries
- A list of program candidates from web search

Your goals:
1. SEPARATE the candidates into TWO categories:
   - **University Programs**: Actual graduate degree programs (MS, PhD, etc.) at specific universities
   - **External Funding**: Fellowships, scholarships, or sponsorships NOT tied to a specific university program
   
2. Pick the BEST {MIN_PROGRAM_RESULTS}-{MAX_PROGRAM_RESULTS} university programs that match their goals.

3. Output THREE sections in MARKDOWN:

Section 1: University Programs Table
Use this header:

| # | Program Name | Degree | University | Location | Tuition, Application Fee & Funding | Key Requirements | Deadline | Program Duration | Intake Term | Website |

ONLY include actual university graduate programs here (MS Data Science at Stanford, PhD in CS at MIT, etc.)
For the Website column, use this EXACT format: [Link](url) with the actual program page URL.

Section 2 (if applicable): Additional Funding Opportunities
If you found external fellowships, scholarships, or sponsorships that are NOT specific university programs:
- List them separately with bullet points
- Include: Name, Eligibility, Amount/Benefits, Deadline, Website link
- Examples: Fulbright, DAAD, government scholarships, private foundations
- Format links as [Fellowship Name](url)

Section 3: My guidance for you
Address the user directly with "you" and "your":
- 5–8 bullet points explaining:
  - why I picked these programs for you
  - trade-offs you should consider (funding vs prestige vs location)
  - if there are external funding opportunities, how you can combine them with programs
  - concrete next steps you should take

Rules:
- CRITICAL: Only put actual university degree programs in the main table
- Move general fellowships/scholarships to the separate "Additional Funding Opportunities" section
- Speak TO the user, not ABOUT them (use "you/your" not "the student/their")
- Be warm and conversational: "You might find X interesting because..." 
- If you're unsure about a detail, write "Check program page" instead of guessing
- Do NOT hallucinate exact deadline days. Month/year is okay if unclear
- Reference their specific profile (your GPA, your test scores, your preferred countries)
- ALWAYS format links as [Link](url) or [Text](url), never paste bare URLs
- Extract and use actual URLs from the raw program candidates provided
"""


def check_if_ready_to_search(
    user_input: str,
    session_id: str,
    store: InMemoryProfileStore,
) -> Dict[str, Any]:
    """
    Determine if we have enough info to search, or need to ask more questions.
    """
    profile = store.get_profile(session_id)
    profile_dict = profile.__dict__
    
    # Debug: Log current memory state
    print(f"[DEBUG] Current profile in memory for session {session_id[:8]}...")
    print(f"[DEBUG] Profile contents: {json.dumps(profile_dict, indent=2)}")
    
    prompt = f"""
{COORDINATOR_SYSTEM_PROMPT}

CURRENT STUDENT PROFILE (JSON):
{json.dumps(profile_dict, indent=2)}

USER'S LATEST MESSAGE:
{user_input}

Now decide: do we have enough information to search for programs?
"""
    
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(prompt)
    
    text = response.text.strip() if response.text else ""
    
    # Clean up markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        if len(lines) > 2:
            text = "\n".join(lines[1:-1])
        if text.startswith("json\n"):
            text = text[5:]
        text = text.strip()
    
    try:
        decision = json.loads(text)
    except json.JSONDecodeError:
        # Default to asking for more info if parsing fails
        decision = {
            "needs_more_info": True,
            "missing_info": ["basic requirements"],
            "questions_to_ask": "I'd love to help you find the perfect graduate programs! Could you tell me a bit more about what you're looking for? Specifically, what field are you interested in, and do you have a GPA and location preference?",
            "ready_to_search": False
        }
    
    # IMPORTANT: Even if we need more info, save any extracted info to memory
    extracted = decision.get("extracted_info", {})
    if extracted:
        print(f"[DEBUG] Coordinator extracted info from message: {extracted}")
        
        # Build profile updates from extracted info
        # Helper function to check if a value should be saved
        def should_save(value):
            if not value:
                return False
            value_lower = str(value).lower()
            # Don't save placeholder strings
            skip_phrases = ["already in profile", "not provided", "unknown", "none", "n/a", "null"]
            return not any(phrase in value_lower for phrase in skip_phrases)
        
        updates = {}
        
        if should_save(extracted.get("field")):
            updates["field_of_study"] = extracted["field"]
        
        if should_save(extracted.get("degree_level")):
            updates["degree_level"] = extracted["degree_level"]
        
        if should_save(extracted.get("location")):
            updates["preferred_countries"] = extracted["location"]
        
        if should_save(extracted.get("gpa")):
            updates["gpa"] = extracted["gpa"]
        
        if should_save(extracted.get("funding_preference")):
            updates["funding_needs"] = extracted["funding_preference"]
        
        # Apply updates to memory
        if updates:
            print(f"[DEBUG] Updating profile with extracted info: {updates}")
            store.update_profile(session_id, **updates)
            updated_profile = store.as_dict(session_id)
            print(f"[DEBUG] Profile after coordinator extraction: {json.dumps(updated_profile, indent=2)}")
    
    return decision


def run_search_queries(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Execute search_queries from the plan using Serper and accumulate candidates.
    """
    search_queries = plan.get("search_queries", []) or []
    all_candidates: List[Dict[str, Any]] = []

    print(f"[DEBUG] Search queries from plan: {search_queries}")
    
    for q in search_queries:
        try:
            print(f"[DEBUG] Executing search for: {q}")
            res = serper_program_search(q, num_results=5)
            extracted = extract_program_candidates(res)
            print(f"[DEBUG] Found {len(extracted)} candidates for query: {q}")
            all_candidates.extend(extracted)
        except Exception as e:
            print(f"[WARN] Search error for query '{q}': {e}")
            continue

    print(f"[DEBUG] Total candidates found: {len(all_candidates)}")
    return all_candidates


def classify_query(user_input: str) -> Dict[str, Any]:
    """
    Classify the user's query to determine if it's a new search, deep dive, or comparison.
    """
    prompt = f"""
{QUERY_CLASSIFIER_PROMPT}

USER MESSAGE:
{user_input}
"""
    
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(prompt)
    text = response.text.strip() if response.text else ""
    
    # Clean up markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        if len(lines) > 2:
            text = "\n".join(lines[1:-1])
        if text.startswith("json\n"):
            text = text[5:]
        text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Default to new_search if classification fails
        return {"query_type": "new_search", "universities": [], "comparison_aspects": [], "notes": ""}


def handle_deep_dive(university_query: str, universities: List[str], store: InMemoryProfileStore, session_id: str) -> str:
    """
    Provide detailed, extensive information about a specific university program.
    """
    # Get student profile to include field of study
    profile = store.get_profile(session_id)
    field = profile.field_of_study or "graduate programs"
    degree = profile.degree_level or "MS"
    
    # Create comprehensive, focused search queries for extensive coverage
    search_queries = []
    for uni in universities[:2]:  # Limit to 2 universities if multiple mentioned
        # Core program information
        search_queries.append(f'"{uni}" {field} {degree} program overview')
        search_queries.append(f'"{uni}" {field} {degree} admission requirements GPA test scores')
        
        # Funding and financial
        search_queries.append(f'"{uni}" {field} {degree} funding RA TA fellowships stipend')
        search_queries.append(f'"{uni}" {field} graduate program scholarships financial aid')
        
        # Application process
        search_queries.append(f'"{uni}" {field} {degree} application deadline process')
        
        # Research and faculty
        search_queries.append(f'"{uni}" {field} research labs faculty')
        
        # Student experience
        search_queries.append(f'"{uni}" {field} {degree} student experience career outcomes')
        
        # Specific details
        if profile.extra_notes and 'healthcare' in profile.extra_notes.lower():
            search_queries.append(f'"{uni}" {field} healthcare applications research')
    
    # Execute MORE searches for comprehensive results (8-10 queries)
    all_results = []
    for query in search_queries[:10]:  # Increased from 3 to 10
        try:
            print(f"[DEBUG] Deep dive search: {query}")
            res = serper_program_search(query, num_results=8)  # Increased from 5 to 8 per query
            all_results.extend(extract_program_candidates(res))
        except Exception as e:
            print(f"[WARN] Search error: {e}")
    
    # Format MORE search results for comprehensive report
    search_results_text = "\n\n".join([
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}"
        for r in all_results[:30]  # Increased from 10 to 30 results
    ])
    
    print(f"[DEBUG] Deep dive: Using {len(all_results[:30])} search results for comprehensive report")
    
    # Generate response with explicit instruction for extensive report
    prompt = DEEP_DIVE_PROMPT.format(
        university_query=university_query,
        search_results=search_results_text or "No specific results found. Provide general guidance based on typical program structure."
    )
    
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(prompt)
    
    # Clean up Unicode escape sequences
    result = response.text
    result = result.replace(r'\u201c', '"')  # Left double quotation mark
    result = result.replace(r'\u201d', '"')  # Right double quotation mark
    result = result.replace(r'\u2018', "'")  # Left single quotation mark
    result = result.replace(r'\u2019', "'")  # Right single quotation mark
    result = result.replace(r'\u2013', '–')  # En dash
    result = result.replace(r'\u2014', '—')  # Em dash
    result = result.replace(r'\u2026', '...')  # Ellipsis
    
    return result


def handle_comparison(universities: List[str], aspects: List[str], store: InMemoryProfileStore, session_id: str) -> str:
    """
    Compare multiple universities on specific aspects.
    """
    # Get student profile to include field of study
    profile = store.get_profile(session_id)
    field = profile.field_of_study or "graduate programs"
    degree = profile.degree_level or "MS"
    
    # Create search queries for comparison with field context
    search_queries = []
    for uni in universities[:3]:  # Limit to 3 universities
        search_queries.append(f'"{uni}" {field} {degree} program funding requirements')
        if aspects:
            for aspect in aspects[:2]:
                search_queries.append(f'"{uni}" {field} {aspect}')
    
    # Execute searches
    all_results = []
    for query in search_queries[:6]:  # Limit total searches
        try:
            print(f"[DEBUG] Comparison search: {query}")
            res = serper_program_search(query, num_results=5)
            all_results.extend(extract_program_candidates(res))
        except Exception as e:
            print(f"[WARN] Search error: {e}")
    
    # Format search results
    search_results_text = "\n\n".join([
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}"
        for r in all_results[:15]
    ])
    
    # Generate response
    prompt = COMPARISON_PROMPT.format(
        universities=", ".join(universities),
        aspects=", ".join(aspects) if aspects else "all aspects",
        search_results=search_results_text or "No specific results found. Provide general comparison."
    )
    
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(prompt)
    
    # Clean up Unicode escape sequences
    result = response.text
    result = result.replace(r'\u201c', '"')  # Left double quotation mark
    result = result.replace(r'\u201d', '"')  # Right double quotation mark
    result = result.replace(r'\u2018', "'")  # Left single quotation mark
    result = result.replace(r'\u2019', "'")  # Right single quotation mark
    result = result.replace(r'\u2013', '–')  # En dash
    result = result.replace(r'\u2014', '—')  # Em dash
    result = result.replace(r'\u2026', '...')  # Ellipsis
    
    return result


def build_writer_prompt(
    profile_dict: Dict[str, Any],
    plan: Dict[str, Any],
    candidates: List[Dict[str, Any]],
) -> str:
    return f"""
SYSTEM:
{WRITER_SYSTEM_PROMPT}

STUDENT PROFILE (JSON):
{json.dumps(profile_dict, indent=2)}

SEARCH PLAN (JSON):
{json.dumps(plan, indent=2)}

RAW PROGRAM CANDIDATES (JSON):
{json.dumps(candidates[:30], indent=2)}

Now produce the Markdown output described above.
"""


def generate_followup_questions(
    profile_dict: Dict[str, Any],
    query_type: str,
    results_summary: str,
    candidates: List[Dict[str, Any]]
) -> List[str]:
    """
    Generate intelligent follow-up questions based on the conversation context.
    
    Args:
        profile_dict: Student profile
        query_type: Type of query (new_search, deep_dive, compare)
        results_summary: Brief summary of what was found
        candidates: List of program candidates found
        
    Returns:
        List of 2-3 follow-up questions
    """
    # Create a summary of results for context
    if not candidates:
        results_info = "No programs found"
    else:
        program_count = len(candidates)
        # Extract university names from titles or domains
        universities = []
        for c in candidates[:10]:
            # Try to extract university from title (e.g., "Program Name - Stanford University")
            title = c.get('title', '')
            # Common patterns: "University of X", "X University", "X Institute"
            if 'University' in title or 'Institute' in title or 'College' in title:
                # Extract the university name from title
                parts = title.split('-')
                if len(parts) > 1:
                    univ = parts[-1].strip()
                else:
                    univ = title
                universities.append(univ)
            elif c.get('source'):
                # Fall back to domain name (e.g., stanford.edu -> Stanford)
                domain = c.get('source', '')
                if domain:
                    # Extract main part of domain (e.g., stanford from stanford.edu)
                    domain_parts = domain.split('.')
                    if len(domain_parts) >= 2:
                        universities.append(domain_parts[-2].title())
        
        # Get unique universities, limit to 5
        unique_universities = list(set([u for u in universities if u]))[:5]
        
        if unique_universities:
            results_info = f"Found {program_count} programs at universities including: {', '.join(unique_universities)}"
        else:
            results_info = f"Found {program_count} programs from various universities"
    
    prompt = FOLLOWUP_GENERATOR_PROMPT.format(
        profile=json.dumps(profile_dict, indent=2),
        query_type=query_type,
        results_summary=results_info
    )
    
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip() if response.text else ""
        
        # Clean up markdown code blocks
        if text.startswith("```"):
            lines = text.split("\n")
            if len(lines) > 2:
                text = "\n".join(lines[1:-1])
            if text.startswith("json"):
                text = text[4:].strip()
        
        result = json.loads(text)
        questions = result.get("follow_up_questions", [])
        
        print(f"[DEBUG] Generated follow-up questions: {questions}")
        return questions[:3]  # Return max 3 questions
        
    except Exception as e:
        print(f"[WARN] Failed to generate follow-up questions: {e}")
        # Return generic but helpful fallback questions
        return [
            "Would you like me to dive deeper into any specific program?",
            "Should I search for programs with different requirements?",
            "Are you interested in comparing specific universities?"
        ]


def execute_agentic_pipeline(
    user_input: str,
    session_id: str,
    store: InMemoryProfileStore,
) -> str:
    """
    End-to-end pipeline:

    1. Classify query type (new search, deep dive, or comparison)
    2. Handle accordingly:
       - Deep dive: Get detailed info about specific university
       - Compare: Compare multiple universities
       - New search: Standard search flow
    """
    # 0) First, classify the query
    classification = classify_query(user_input)
    query_type = classification.get("query_type", "new_search")
    
    print(f"[DEBUG] Query classified as: {query_type}")
    print(f"[DEBUG] Classification details: {classification}")
    
    # Handle deep dive queries
    if query_type == "deep_dive":
        universities = classification.get("universities", [])
        if universities:
            main_response = handle_deep_dive(user_input, universities, store, session_id)
            
            # Add follow-up questions for deep dive
            profile_dict = store.as_dict(session_id)
            followup_questions = [
                f"Would you like to compare {universities[0]} with other similar universities?",
                f"Should I search for more programs in the same field at other universities?",
                f"Are you interested in learning about application strategies for {universities[0]}?"
            ]
            
            followup_section = "\n\n---\n\n### 💡 What would you like to explore next?\n\n"
            for i, question in enumerate(followup_questions, 1):
                followup_section += f"{i}. {question}\n"
            
            return main_response + followup_section
        # Fallback to new search if no universities identified
    
    # Handle comparison queries
    if query_type == "compare":
        universities = classification.get("universities", [])
        aspects = classification.get("comparison_aspects", [])
        if len(universities) >= 2:
            main_response = handle_comparison(universities, aspects, store, session_id)
            
            # Add follow-up questions for comparison
            profile_dict = store.as_dict(session_id)
            followup_questions = [
                f"Would you like a detailed breakdown of the application process for these programs?",
                f"Should I find more universities similar to your top choice?",
                f"Are you interested in learning about student experiences at these universities?"
            ]
            
            followup_section = "\n\n---\n\n### 💡 What would you like to explore next?\n\n"
            for i, question in enumerate(followup_questions, 1):
                followup_section += f"{i}. {question}\n"
            
            return main_response + followup_section
        # Fallback to new search if comparison not possible
    
    # Standard new search flow
    # 1) Check if we're ready to search or need more info
    decision = check_if_ready_to_search(user_input, session_id, store)
    
    if decision.get("needs_more_info") and not decision.get("ready_to_search"):
        # Return the questions to gather more information
        return decision.get("questions_to_ask", "Could you provide more details about what you're looking for?")
    
    # 2) We have enough info - proceed with search
    # Import here to avoid circular import
    from .planner import plan_from_user_input

    # Plan + update memory
    plan = plan_from_user_input(user_input, session_id, store)
    print(f"[DEBUG] Generated plan: {json.dumps(plan, indent=2)}")

    # Run web search
    candidates = run_search_queries(plan)
    print(f"[DEBUG] Total candidates after all searches: {len(candidates)}")

    # Build writer prompt & call Gemini to synthesize final answer
    profile_dict = store.as_dict(session_id)
    writer_prompt = build_writer_prompt(profile_dict, plan, candidates)

    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(writer_prompt)
    
    main_response = response.text
    
    # Clean up Unicode escape sequences in the response
    # Replace common Unicode escapes with actual characters
    main_response = main_response.replace(r'\u201c', '"')  # Left double quotation mark
    main_response = main_response.replace(r'\u201d', '"')  # Right double quotation mark
    main_response = main_response.replace(r'\u2018', "'")  # Left single quotation mark
    main_response = main_response.replace(r'\u2019', "'")  # Right single quotation mark
    main_response = main_response.replace(r'\u2013', '–')  # En dash
    main_response = main_response.replace(r'\u2014', '—')  # Em dash
    main_response = main_response.replace(r'\u2026', '...')  # Ellipsis
    
    # Generate intelligent follow-up questions
    followup_questions = generate_followup_questions(
        profile_dict=profile_dict,
        query_type=query_type,
        results_summary=f"Found {len(candidates)} programs",
        candidates=candidates
    )
    
    # Append follow-up questions to the response
    if followup_questions:
        followup_section = "\n\n---\n\n### 💡 What would you like to explore next?\n\n"
        for i, question in enumerate(followup_questions, 1):
            followup_section += f"{i}. {question}\n"
        
        main_response += followup_section
    
    return main_response

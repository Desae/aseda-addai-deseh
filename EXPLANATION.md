# Technical Explanation

This document provides a comprehensive technical explanation of the **Adaptive Agentic Search Assistant (GradPath)**, a multi-agent system designed to help students find graduate programs through personalized, context-aware search.

---

## 1. Agent Workflow

The system follows a multi-stage agentic pipeline that processes each user input through several specialized agents:

### High-Level Flow

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  1. COORDINATOR AGENT                                   │
│     • Analyzes user intent                              │
│     • Extracts profile information from message         │
│     • Decides: need more info? or ready to search?      │
│     • Updates memory immediately with extracted info    │
└─────────────────────────────────────────────────────────┘
    │
    ▼ (if ready to search)
┌─────────────────────────────────────────────────────────┐
│  2. QUERY CLASSIFIER AGENT                              │
│     • Classifies query type:                            │
│       - "new_search" → find programs matching criteria  │
│       - "deep_dive" → detailed info on specific program │
│       - "compare" → compare multiple programs           │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  3. PLANNER AGENT                                       │
│     • Creates search strategy based on profile          │
│     • Generates 3-5 optimized search queries            │
│     • Updates profile with any new information          │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  4. SEARCH EXECUTOR                                     │
│     • Calls Serper API for each query                   │
│     • Rate limiting (0.5s delay between calls)          │
│     • Extracts and deduplicates results                 │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  5. WRITER AGENT                                        │
│     • Synthesizes results into coherent response        │
│     • Personalizes based on user profile                │
│     • Adds references and source links                  │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  6. FOLLOW-UP GENERATOR AGENT                           │
│     • Analyzes conversation context                     │
│     • Generates 2-3 intelligent follow-up questions     │
│     • Personalizes based on profile and results         │
└─────────────────────────────────────────────────────────┘
    │
    ▼
Final Response (with references and follow-up questions)
```

### Step-by-Step Processing

#### Step 1: Receive User Input
```python
# From streamlit_app.py
user_input = st.chat_input("Ask me anything about graduate programs...")
```

#### Step 2: Memory Retrieval
```python
# From executor.py - check_if_ready_to_search()
profile = profile_store.get_profile(session_id)
profile_dict = profile_store.as_dict(session_id)
```
The system retrieves the user's existing profile containing:
- GPA, GRE, IELTS/TOEFL scores
- Field of study and degree level
- Preferred countries/cities
- Funding needs and budget
- Target intake term

#### Step 3: Coordinator Analysis
The Coordinator agent uses Gemini to analyze the message and extract new information:
```python
# Coordinator extracts info and decides next step
coordinator_response = {
    "needs_more_info": false,
    "ready_to_search": true,
    "extracted_info": {
        "field": "Data Science",
        "degree_level": "Master's",
        "location": "USA",
        "funding_preference": "fully funded"
    }
}
```

#### Step 4: Query Classification
```python
# From executor.py - classify_query()
classification = {
    "query_type": "new_search",  # or "deep_dive" or "compare"
    "universities": [],
    "comparison_aspects": []
}
```

#### Step 5: Planning (for new_search)
```python
# From planner.py - plan_from_user_input()
search_plan = {
    "high_level_goal": "Find PhD Machine Learning programs in USA with healthcare focus and full funding",
    "search_queries": [
        "PhD Machine Learning USA",  # General programs
        "Machine Learning PhD funding scholarships",  # Funding-specific
        "PhD Machine Learning admission requirements",  # Requirements
        "Machine Learning healthcare AI PhD",  # Specialty focus
        "PhD Machine Learning Fall 2026 fully funded"  # Specific intake
    ],
    "profile_updates": {
        "field_of_study": "Machine Learning",
        "degree_level": "PhD",
        "preferred_countries": "US",
        "gpa": "3.7",
        "funding_needs": "full funding",
        "intake_term": "Fall 2026",
        "extra_notes": "Interested in healthcare applications"
    }
}
# Planner generates 5-7 targeted queries with specific purposes:
# - Queries 1-2: General program pages
# - Queries 3-4: Funding-specific searches
# - Queries 5-6: Requirements/admissions
# - Query 7: Specialty focus if applicable
```

#### Step 6: Tool Execution (Serper API)
```python
# From tools/search.py - serper_program_search()
for query in search_queries:
    results = serper_program_search(query, num_results=10)
    time.sleep(0.5)  # Rate limiting
```

#### Step 7: Response Synthesis
The Writer agent combines results into a personalized response with THREE sections:

**Section 1: University Programs Table**
- Only actual graduate degree programs (MS, PhD) at specific universities
- Columns: Program Name, Degree, University, Location, Funding, Requirements, Deadline, Duration, Intake, Website
- Direct links to program pages

**Section 2: Additional Funding Opportunities (if applicable)**
- External fellowships, scholarships not tied to specific programs
- Examples: Fulbright, DAAD, government scholarships
- Listed separately with eligibility and links

**Section 3: Personalized Guidance**
- 5-8 bullet points explaining program recommendations
- Trade-offs to consider (funding vs prestige vs location)
- How to combine external funding with programs
- Concrete next steps

#### Step 8: Follow-up Question Generation
```python
# From executor.py - generate_followup_questions()
followups = {
    "follow_up_questions": [
        "Would you like me to compare Carnegie Mellon and Cedars-Sinai programs?",
        "Should I search for programs in Germany?",
        "Are you interested in learning about application strategies?"
    ]
}
# Questions are contextual and personalized based on:
# - Student profile (GPA, field, preferences)
# - Query type (new_search, deep_dive, compare)
# - Results found (specific universities mentioned)
```

---

## 2. Key Modules

### **Coordinator** (`executor.py` - `check_if_ready_to_search()`)

The Coordinator is the first agent in the pipeline, responsible for:

1. **Intent Understanding**: Analyzes what the user wants
2. **Information Extraction**: Pulls profile data from natural language
3. **Completeness Check**: Determines if enough info exists to search
4. **Memory Update**: Saves extracted info immediately (even when asking questions)

```python
COORDINATOR_SYSTEM_PROMPT = """
You are the GradPath Coordinator. Your job is to decide whether you have 
enough information to search for programs, or if you need to ask more questions.

MINIMUM REQUIRED INFO:
- Field of study (either from profile OR current message)
- Degree level (either from profile OR current message)

Output JSON with:
- needs_more_info: boolean
- missing_info: list of what's missing
- questions_to_ask: friendly follow-up question
- ready_to_search: boolean
- extracted_info: {field, degree_level, location, gpa, funding_preference}
"""
```

**Key Feature**: The coordinator extracts and saves information immediately, even when asking follow-up questions. This prevents the "asking twice" problem.

---

### **Query Classifier** (`executor.py` - `classify_query()`)

Routes queries to the appropriate handler:

| Query Type | Trigger Examples | Handler |
|------------|------------------|---------|
| `new_search` | "Find MS programs in AI" | Full planner → search pipeline |
| `deep_dive` | "Tell me more about Stanford" | Single-program research |
| `compare` | "Compare MIT vs CMU" | Side-by-side comparison |

```python
QUERY_CLASSIFIER_PROMPT = """
Types:
1. "deep_dive" - User wants more details about a specific program
2. "compare" - User wants to compare multiple universities  
3. "new_search" - User wants to search for new programs
"""
```

---

### **Planner** (`planner.py`)

Creates optimized search strategies based on user profile:

```python
def plan_from_user_input(user_input: str, session_id: str, profile_store: InMemoryProfileStore):
    profile = profile_store.get_profile(session_id)
    
    # Build prompt with current profile
    prompt = build_planner_prompt(user_input, profile)
    
    # Get Gemini to create search plan
    response = model.generate_content(prompt)
    plan = json.loads(response.text)
    
    # Update profile with new information
    if plan.get("profile_updates"):
        profile_store.update_profile(session_id, **plan["profile_updates"])
    
    return plan
```

**Output Structure**:
```json
{
  "high_level_goal": "Find fully funded MS Data Science programs",
  "profile_updates": {"field_of_study": "Data Science", "degree_level": "MS"},
  "filters": {
    "field_of_study": "Data Science",
    "degree_type": ["MS", "MSc"],
    "countries_or_regions": ["USA", "Canada"],
    "funding_priority": ["RA", "TA", "scholarship"]
  },
  "search_queries": [
    "MS Data Science fully funded USA",
    "Data Science graduate scholarships Canada",
    "Master Data Science no GRE funding"
  ]
}
```

---

### **Executor** (`executor.py`)

The main orchestration module containing:

1. **Pipeline Orchestration**: `execute_agentic_pipeline()`
2. **Coordinator Logic**: `check_if_ready_to_search()`
3. **Query Classification**: `classify_query()`
4. **Handler Functions**: `handle_deep_dive()`, `handle_comparison()`
5. **Search Execution**: `execute_search_plan()`
6. **Response Writing**: `write_search_results()`
7. **Follow-up Generation**: `generate_followup_questions()`

```python
def execute_agentic_pipeline(
    user_input: str,
    session_id: str,
    profile_store: InMemoryProfileStore,
    conversation_history: List[Dict] = None
) -> str:
    # 1. Check if ready to search (Coordinator)
    ready_result = check_if_ready_to_search(user_input, session_id, profile_store)
    
    if not ready_result["ready_to_search"]:
        return ready_result["response"]
    
    # 2. Classify query type
    classification = classify_query(user_input, conversation_history)
    
    # 3. Route to appropriate handler
    if classification["query_type"] == "deep_dive":
        response = handle_deep_dive(...)
    elif classification["query_type"] == "compare":
        response = handle_comparison(...)
    else:
        # 4. Plan search strategy
        plan = plan_from_user_input(user_input, session_id, profile_store)
        
        # 5. Execute searches
        results = execute_search_plan(plan)
        
        # 6. Write response
        response = write_search_results(results, profile_store.as_dict(session_id))
    
    # 7. Generate follow-up questions
    followups = generate_followup_questions(...)
    
    return response + followups
```

---

### **Memory Store** (`memory.py`)

Persistent user profile storage using a dataclass-based approach:

```python
@dataclass
class StudentProfile:
    """Represents what GradPath knows about the student."""
    gpa: Optional[str] = None
    gre: Optional[str] = None
    ielts: Optional[str] = None
    toefl: Optional[str] = None
    field_of_study: Optional[str] = None
    degree_level: Optional[str] = None
    preferred_countries: Optional[str] = None
    preferred_cities: Optional[str] = None
    funding_needs: Optional[str] = None
    intake_term: Optional[str] = None
    budget_notes: Optional[str] = None
    extra_notes: Optional[str] = None


class InMemoryProfileStore:
    """Session-based profile storage."""
    
    def get_profile(self, session_id: str) -> StudentProfile:
        if session_id not in self._profiles:
            self._profiles[session_id] = StudentProfile()
        return self._profiles[session_id]
    
    def update_profile(self, session_id: str, **updates) -> StudentProfile:
        profile = self.get_profile(session_id)
        for key, value in updates.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)
        return profile
```

**Session Isolation**: Each chat session has its own profile, preventing context bleed between conversations.

---

## 3. Tool Integration

### **Serper API** (Web Search)

Primary tool for real-time web search:

```python
# src/tools/search.py

def serper_program_search(
    query: str,
    num_results: int = 10,
    country: Optional[str] = None,
    locale: str = "en"
) -> Dict[str, Any]:
    """
    Call Serper.dev to run a Google search.
    """
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }
    
    payload = {
        "q": query,
        "num": num_results,
        "hl": locale,
    }
    if country:
        payload["gl"] = country
    
    resp = requests.post(
        SERPER_SEARCH_URL,
        headers=headers,
        data=json.dumps(payload),
        timeout=20
    )
    
    return resp.json()
```

**Result Extraction**:
```python
def extract_program_candidates(serper_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract structured candidates from Serper response."""
    organic = serper_json.get("organic", [])
    candidates = []
    
    for item in organic:
        candidates.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
            "source": urlparse(item.get("link", "")).netloc
        })
    
    return candidates
```

**Rate Limiting**: 0.5 second delay between API calls to prevent throttling.

---

### **Google Gemini API** (LLM Reasoning)

Used for all agent reasoning and text generation:

```python
# Configuration
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)

# Model: gemini-2.0-flash-exp
model = genai.GenerativeModel(GEMINI_MODEL_NAME)

# Usage
response = model.generate_content(prompt)
result = response.text
```

**Applications**:
| Agent | Gemini Usage |
|-------|--------------|
| Coordinator | Intent analysis, information extraction |
| Classifier | Query type classification |
| Planner | Search strategy generation |
| Writer | Response synthesis |
| Follow-up Generator | Contextual question generation |

---

### **Streamlit** (UI Framework)

Interactive web interface with session management:

```python
# Session state management
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

# Multi-session support
def create_new_session():
    session_id = str(uuid.uuid4())
    st.session_state.chat_sessions[session_id] = {
        "title": "New Chat",
        "messages": [],
        "research_mode": False,
        "created_at": datetime.now()
    }
    return session_id
```

---

## 4. Observability & Testing

### Debug Logging

Comprehensive logging throughout the pipeline:

```python
# Search execution logging
print(f"[DEBUG] Serper API response keys: {result.keys()}")
print(f"[DEBUG] Number of organic results: {len(result.get('organic', []))}")

# Memory operations logging
print(f"[MEMORY DEBUG] Session ID: {session_id}")
print(f"[MEMORY DEBUG] Current profile before update: {profile_dict}")
print(f"[MEMORY DEBUG] Extracted info to save: {extracted_info}")

# Pipeline stage logging
print(f"[COORDINATOR] Ready to search: {ready_result['ready_to_search']}")
print(f"[CLASSIFIER] Query type: {classification['query_type']}")
print(f"[PLANNER] Generated {len(plan['search_queries'])} queries")
```

### Tracing Agent Decisions

Each agent outputs structured JSON that can be inspected:

```python
# Coordinator decision trace
{
    "needs_more_info": false,
    "missing_info": [],
    "ready_to_search": true,
    "extracted_info": {
        "field": "Data Science",
        "degree_level": "Master's"
    }
}

# Planner decision trace
{
    "high_level_goal": "Find MS Data Science programs with funding",
    "search_queries": ["query1", "query2", "query3"],
    "profile_updates": {"field_of_study": "Data Science"}
}
```

### Testing

**`TEST.sh`** - Main test script:
```bash
#!/bin/bash
# Test the main agentic pipeline

# Set environment variables
export GOOGLE_API_KEY="your-key"
export SERPER_API_KEY="your-key"

# Run the Streamlit app
streamlit run streamlit_app.py
```

**Manual Testing Scenarios**:

1. **Basic Search Flow**:
   - Input: "I'm looking for MS programs in Data Science"
   - Expected: Coordinator asks for location/funding preferences
   - Input: "USA, fully funded"
   - Expected: Search results with program recommendations

2. **Memory Persistence**:
   - Input: "I have a 3.5 GPA"
   - Expected: GPA saved to profile
   - Input: "Show me programs"
   - Expected: Search uses GPA from memory (no re-asking)

3. **Deep Dive**:
   - After search results, Input: "Tell me more about Stanford"
   - Expected: Detailed single-program research

4. **Comparison**:
   - Input: "Compare MIT and CMU"
   - Expected: Side-by-side comparison table

---

## 5. Known Limitations

### API Rate Limiting
- **Serper API**: Limited requests per month on free tier
- **Mitigation**: 0.5s delay between calls, query optimization

### Memory Persistence
- **Current**: In-memory storage (lost on app restart)
- **Limitation**: No persistent storage across server restarts
- **Future**: Could add Redis/PostgreSQL for persistence

### Search Query Optimization
- **Issue**: Overly specific queries can return 0 results
- **Mitigation**: Planner trained to generate simple, natural queries
- **Ongoing**: Balance between specificity and result coverage

### LLM Response Parsing
- **Issue**: Gemini sometimes returns markdown-wrapped JSON
- **Mitigation**: JSON extraction with regex fallback
```python
def extract_json_from_response(text: str) -> dict:
    # Try direct parse
    try:
        return json.loads(text)
    except:
        # Extract from markdown code block
        match = re.search(r'```(?:json)?\s*(.*?)```', text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise ValueError("Could not parse JSON")
```

### Ambiguous Queries
- **Issue**: Queries like "Python" could mean programming or snakes
- **Mitigation**: Coordinator asks clarifying questions
- **Example**: "Are you interested in Python programming or Python snakes?"

### Session Isolation
- **Current**: Each chat session has independent memory
- **Limitation**: No cross-session profile merging
- **Trade-off**: Privacy vs. convenience

### Real-time Data Accuracy
- **Issue**: Graduate program info changes (deadlines, requirements)
- **Mitigation**: Search provides real-time web results
- **Recommendation**: Users should verify with official sources

---

## 6. Architecture Decisions

### Why Multi-Agent vs. Single Agent?
- **Separation of Concerns**: Each agent specializes in one task
- **Debuggability**: Easy to trace which agent made which decision
- **Flexibility**: Can modify/replace individual agents
- **Quality**: Specialized prompts perform better than general ones

### Why Gemini 2.0 Flash?
- **Speed**: Fast response times for interactive chat
- **Cost**: More economical than larger models
- **Quality**: Sufficient for reasoning and planning tasks
- **JSON Mode**: Good at structured output generation

### Why Session-Based Memory?
- **Privacy**: Users don't share profiles
- **Context Isolation**: No confusion between different searches
- **Simplicity**: Clean state management

### Why Serper over Google Search API?
- **Simplicity**: Single API call, JSON response
- **Cost**: Competitive pricing for search
- **Quality**: Google search results without complexity

---

## 7. Future Improvements

1. **Persistent Storage**: Add database backend for profile persistence
2. **RAG Integration**: Index university websites for deeper knowledge
3. **Application Tracking**: Track deadlines and application status
4. **Document Analysis**: Parse uploaded transcripts/CVs
5. **Email Alerts**: Notify users of approaching deadlines
6. **Collaborative Features**: Share searches with advisors
7. **Analytics Dashboard**: Track search patterns and popular programs

---

## Summary

The Adaptive Agentic Search Assistant demonstrates key agentic AI patterns:

| Pattern | Implementation |
|---------|----------------|
| **Multi-Agent Collaboration** | Coordinator → Classifier → Planner → Searcher → Writer |
| **Memory Integration** | Session-based profiles with immediate extraction |
| **Tool Use** | Serper API for web search, Gemini for reasoning |
| **Adaptive Behavior** | Query classification routes to appropriate handlers |
| **Human-in-the-Loop** | Coordinator asks clarifying questions when needed |
| **Observability** | Debug logging and structured JSON outputs |

The system provides a personalized, intelligent research assistant that learns from each interaction and adapts its search strategies to user needs.  


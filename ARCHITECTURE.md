# GradPath Architecture Documentation

## System Overview

GradPath is an intelligent agentic AI system designed to help students find the perfect graduate programs. It uses Google's Gemini 2.0 Flash model for reasoning and planning, combined with web search capabilities to provide personalized, comprehensive program recommendations.

---

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                          │
│                                                                         │
│  ┌──────────────────────┐              ┌─────────────────────────────┐ │
│  │  Streamlit Web UI    │              │   ADK Playground Ready      │ │
│  │  - Multi-session     │              │   (root_agent.py)           │ │
│  │  - Chat history      │              │   - handle_message()        │ │
│  │  - Research modes    │              │   - Session management      │ │
│  └──────────┬───────────┘              └──────────────┬──────────────┘ │
│             │                                          │                │
│             └──────────────────┬───────────────────────┘                │
│                                ▼                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            AGENT CORE LAYER                             │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │                      COORDINATOR (Executor)                        ││
│  │  - Classifies query type (new_search/deep_dive/compare)           ││
│  │  - Checks if ready to search (collects missing info)              ││
│  │  - Routes to appropriate handler                                  ││
│  │  - Generates follow-up questions                                  ││
│  └──────────────────┬─────────────────────────────────────────────────┘│
│                     │                                                   │
│     ┌───────────────┼───────────────┬──────────────────┐               │
│     ▼               ▼               ▼                  ▼               │
│  ┌─────────┐   ┌─────────┐    ┌──────────────┐                        │
│  │Standard │   │Deep Dive│    │ Comparison   │                        │
│  │ Search  │   │ Handler │    │   Handler    │                        │
│  │Pipeline │   │         │    │              │                        │
│  └────┬────┘   └────┬────┘    └──────┬───────┘                        │
│       │             │                │                                 │
│       │        ┌────▼────────────────▼────┐                            │
│       │        │       PLANNER             │                            │
│       │        │       (Gemini)            │                            │
│       │        │                           │                            │
│       │        │ - Extracts info from user message                    │
│       │        │ - Updates student profile                            │
│       │        │ - Generates search queries                           │
│       │        │ - Creates search plan                                │
│       │        └────┬──────────────────────┘                           │
│       │             │                                                  │
│       │        ┌────▼─────────┐                                        │
│       │        │   EXECUTOR   │                                        │
│       │        │              │                                        │
│       └────────► - Runs search queries                                │
│                │ - Collects candidates                                │
│                │ - Synthesizes results                                │
│                └────┬─────────┘                                        │
│                     │                                                  │
└─────────────────────┼──────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        MEMORY & STATE LAYER                             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              InMemoryProfileStore (memory.py)                     │  │
│  │                                                                   │  │
│  │  Session-based profile storage:                                  │  │
│  │  {                                                               │  │
│  │    "session-id-1": {                                             │  │
│  │      gpa: 3.4,                                                   │  │
│  │      field_of_study: "Data Science",                             │  │
│  │      degree_level: "Master's",                                   │  │
│  │      preferred_countries: "USA, Canada",                         │  │
│  │      funding_needs: "fully funded",                              │  │
│  │      ...                                                         │  │
│  │    }                                                             │  │
│  │  }                                                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              Chat Session Store (Streamlit)                       │  │
│  │                                                                   │  │
│  │  Multi-session chat history:                                     │  │
│  │  {                                                               │  │
│  │    "session-id-1": {                                             │  │
│  │      title: "I have 3.4 GPA...",                                 │  │
│  │      messages: [...],                                            │  │
│  │      research_mode: "Quick Search"                               │  │
│  │    }                                                             │  │
│  │  }                                                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       TOOLS & EXTERNAL APIs                             │
│                                                                         │
│  ┌─────────────────────┐         ┌──────────────────────────────────┐  │
│  │  Google Gemini API  │         │       Serper Search API          │  │
│  │  (gemini-2.0-flash) │         │                                  │  │
│  │                     │         │  - Web search for programs       │  │
│  │  - Query classification       │  - 5 results per query           │  │
│  │  - Information extraction     │  - Rate limiting (0.5s delay)    │  │
│  │  - Search planning  │         │  - Organic results extraction    │  │
│  │  - Result synthesis │         │                                  │  │
│  │  - Follow-up generation       │                                  │  │
│  └─────────────────────┘         └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     OBSERVABILITY & MONITORING                          │
│                                                                         │
│  - Debug logging ([DEBUG] prefixes)                                    │
│  - Profile state tracking                                              │
│  - Search query logging                                                │
│  - Candidate count monitoring                                          │
│  - Error handling with fallbacks                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Breakdown

### 1. User Interface Layer

#### **Streamlit Web UI** (`streamlit_app.py`)
- **Multi-Session Management**: ChatGPT-style interface with multiple independent chat sessions
- **Features**:
  - ➕ New Chat button for starting fresh conversations
  - 🔵/⚪ Active/inactive session indicators
  - 🗑️ Delete unwanted chat sessions
  - 🔄 Refresh button to view current memory state
  - Auto-naming from first user message
  - Real-time profile display in sidebar
  - Session-isolated memory (each chat maintains its own profile)

#### **ADK Playground Integration** (`root_agent.py`)
- Simple entry point: `handle_message(user_input, session_id)`
- Compatible with Google's Agent Development Kit
- Ready for deployment to ADK Playground

---

### 2. Agent Core Layer

#### **A. Coordinator (executor.py)**

**Primary Responsibilities**:
1. **Query Classification**: Determines query type using Gemini
   - `new_search`: Standard program search
   - `deep_dive`: Detailed information about specific university
   - `compare`: Side-by-side comparison of multiple universities

2. **Readiness Check**: Validates if enough information is collected
   - Minimum required: field_of_study + degree_level
   - Extracts information from current user message
   - Updates profile memory immediately
   - Asks follow-up questions if information missing

3. **Routing**: Directs to appropriate handler
   - Deep Dive → `handle_deep_dive()`
   - Comparison → `handle_comparison()`
   - Standard Search → Planner → Executor pipeline

4. **Follow-up Generation**: Creates intelligent contextual questions
   - Personalized to student profile
   - Based on search results
   - Encourages deeper exploration

**Key Prompts**:
- `COORDINATOR_SYSTEM_PROMPT`: Information gathering logic
- `QUERY_CLASSIFIER_PROMPT`: Query type detection
- `FOLLOWUP_GENERATOR_PROMPT`: Smart question generation

#### **B. Planner (planner.py)**

**Responsibilities**:
1. **Profile Extraction**: Parses user messages for profile details
   - GPA, test scores (GRE, TOEFL, IELTS)
   - Field of study, degree level
   - Location preferences, funding needs
   - Timeline, budget constraints

2. **Profile Updates**: Maintains student context in memory
   ```python
   profile_updates = {
       "gpa": "3.4",
       "field_of_study": "Data Science",
       "degree_level": "Master's",
       "preferred_countries": "USA, Canada",
       "funding_needs": "fully funded"
   }
   store.update_profile(session_id, **profile_updates)
   ```

3. **Search Query Generation**: Creates effective web search queries
   - 2-5 queries per search
   - Optimized for program discovery
   - Avoids over-constraining (learned from iterations)
   - Examples:
     - "MS Data Science fully funded USA"
     - "Data Science graduate programs scholarships"
     - "MS Data Science funding Canada"

4. **Search Plan Creation**: Structured plan with filters
   ```json
   {
     "high_level_goal": "Find MS Data Science programs...",
     "filters": {
       "field_of_study": "Data Science",
       "degree_type": ["MS", "MSc"],
       "countries_or_regions": ["USA", "Canada"],
       "funding_priority": ["RA", "TA", "scholarship"]
     },
     "search_queries": [...]
   }
   ```

**Powered by**: Google Gemini 2.0 Flash

#### **C. Search Executor (executor.py + tools/search.py)**

**Search Pipeline**:
1. **Query Execution**: Runs search queries via Serper API
   - 5 results per query
   - Rate limiting (0.5s delay between searches)
   - Error handling with fallback

2. **Candidate Collection**: Extracts program information
   ```python
   {
     "title": "Stanford MS in Computer Science",
     "url": "https://cs.stanford.edu/admissions",
     "snippet": "Application requirements: GPA 3.5+...",
     "university": "Stanford University"
   }
   ```

3. **Result Synthesis**: Gemini generates final response
   - Separates results into:
     * **University Programs**: Actual degree programs (MS/PhD) at specific universities
     * **External Funding**: Fellowships/scholarships not tied to specific programs
   - Filters top 5-10 university programs
   - Creates THREE sections:
     
     **Section 1: University Programs Table**
     - Program Name, Degree, University
     - Location, Funding Info
     - Requirements, Deadlines, Duration, Intake
     - Website links to actual program pages
     
     **Section 2: Additional Funding Opportunities** (if found)
     - External fellowships (Fulbright, DAAD, etc.)
     - Eligibility, amount, deadlines
     - Separate from program listings
     
     **Section 3: Personalized Guidance**
     - Why these programs fit your profile
     - Trade-offs to consider
     - How to combine external funding
     - Concrete next steps
   
   - Includes intelligent follow-up questions

**Writer Output Format**:
```markdown
## 🎓 University Programs

| # | Program Name | Degree | University | Location | Funding | Requirements | Deadline | Website |
|---|--------------|--------|------------|----------|---------|--------------|----------|---------|
| 1 | PhD Machine Learning | PhD | Stanford | CA, USA | Full RA/TA | GPA 3.5+ | Dec 15 | [Link](url) |

## 💰 Additional Funding Opportunities

- **Fulbright Foreign Student Program**: Full funding for international students...
- **DAAD Scholarship**: German government funding for PhD students...

### My guidance for you:
- I picked these programs because...
- You should consider the trade-off between...
- Next steps you should take:
  1. Visit the program websites...
  2. Prepare your application materials...

---

### 💡 What would you like to explore next?
1. Would you like me to compare funding at Stanford vs MIT?
2. Should I search for programs with later deadlines?
3. Are you interested in learning about GRE waivers?
```

#### **D. Specialized Handlers**

**Deep Dive Handler** (`handle_deep_dive()`):
- Triggered by: "Tell me more about Stanford", "CMU program details"
- Searches: University-specific + field-specific
- Output: Detailed breakdown of single program
  - Program Overview
  - Admission Requirements
  - Funding Options
  - Application Details
  - Unique Features
  - References with links

**Comparison Handler** (`handle_comparison()`):
- Triggered by: "Compare MIT and Stanford", "Difference between..."
- Searches: Each university + comparison aspects
- Output: Side-by-side analysis
  - Comparison Table
  - Key Differences
  - Recommendations based on profile
  - References per university

---

### 3. Memory & State Layer

#### **InMemoryProfileStore** (`memory.py`)

**Structure**:
```python
@dataclass
class StudentProfile:
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
```

**Operations**:
- `get_profile(session_id)`: Retrieve profile
- `update_profile(session_id, **kwargs)`: Update fields
- `as_dict(session_id)`: Export as dictionary

**Session Isolation**: Each session has independent profile

#### **Chat Session Store** (Streamlit `st.session_state`)

**Structure**:
```python
{
  "session-uuid": {
    "id": "uuid...",
    "title": "I have a 3.4 GPA and want...",
    "created_at": "2025-12-13T10:30:00",
    "messages": [
      {"role": "assistant", "content": "Welcome..."},
      {"role": "user", "content": "I have 3.4 GPA..."},
      {"role": "assistant", "content": "Great! Here are..."}
    ],
    "research_mode": "Quick Search"
  }
}
```

**Features**:
- Multiple sessions preserved simultaneously
- Auto-naming from first user message
- Independent research mode per session
- Message history preserved
- Session switching without data loss

---

### 4. Tools & External APIs

#### **Google Gemini API** (gemini-2.0-flash-exp)

**Usage Throughout System**:
1. **Coordinator**: Query classification, readiness checks
2. **Planner**: Profile extraction, search query generation
3. **Writer**: Result synthesis, response formatting
4. **Follow-up Generator**: Intelligent question creation

**Configuration**:
```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")
model = genai.GenerativeModel(GEMINI_MODEL_NAME)
```

**Key Features Used**:
- Content generation
- JSON output parsing
- Context understanding
- Multi-turn reasoning

#### **Serper Search API**

**Purpose**: Real-time web search for graduate programs

**Implementation** (`tools/search.py`):
```python
def serper_program_search(query: str, num_results: int = 5):
    payload = {
        "q": query,
        "num": num_results,
        "gl": "us"
    }
    response = requests.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": SERPER_API_KEY},
        json=payload
    )
    return response.json()
```

**Result Extraction**:
- Organic search results
- Title, URL, snippet
- University identification
- Debug logging for monitoring

**Rate Limiting**: 0.5s delay between searches

---

### 5. Observability & Monitoring

#### **Debug Logging System**

**Throughout Codebase**:
```python
print(f"[DEBUG] Current profile: {json.dumps(profile_dict, indent=2)}")
print(f"[DEBUG] Search queries from plan: {search_queries}")
print(f"[DEBUG] Total candidates found: {len(candidates)}")
print(f"[RESEARCH PROGRESS] 🔍 Analyzing your question...")
```

**Key Monitoring Points**:
1. **Profile Updates**: Before/after state logging
2. **Search Execution**: Query logging, result counts
3. **Query Classification**: Type detection results
4. **Memory State**: Profile contents at each step
5. **Error Handling**: Graceful fallbacks with warnings

#### **Error Handling**

**Strategies**:
- JSON parsing fallbacks
- Default plans when parsing fails
- Search error handling (continue on failure)
- Profile extraction defaults
- User-friendly error messages

**Example**:
```python
try:
    plan = json.loads(text)
except json.JSONDecodeError:
    print("[ERROR] Failed to parse JSON")
    plan = generate_fallback_plan()
```

---

## Data Flow Example

### Scenario: User searches for "MS Data Science programs with funding"

```
1. USER INPUT
   ↓
   "I have a 3.4 GPA and want MS Data Science programs with funding in USA"

2. COORDINATOR
   ↓
   - Classifies as "new_search"
   - Extracts: GPA=3.7, field=Machine Learning, degree=PhD, location=US, funding=full, focus=healthcare
   - Updates profile in memory
   - Checks readiness → HAS: field + degree + location → Ready to search!

3. PLANNER (Gemini API)
   ↓
   - Receives: user message + current profile
   - Generates search plan with 5-7 structured queries:
     * Profile updates
     * Filters (field, degree, country, funding, healthcare focus)
     * Search queries: [
         "PhD Machine Learning USA",  # General programs
         "Machine Learning PhD funding scholarships",  # Funding-specific
         "PhD Machine Learning admission requirements",  # Requirements
         "Machine Learning healthcare AI PhD",  # Specialty focus
         "PhD Machine Learning Fall 2026 fully funded"  # Specific intake
       ]

4. SEARCH EXECUTOR
   ↓
   - Executes 5-7 searches via Serper API
   - Collects ~20-30 program candidates
   - Each has: title, URL, snippet, university

5. WRITER (Gemini API)
   ↓
   - Receives: profile + plan + candidates
   - Separates university programs from external funding
   - Synthesizes THREE-section response:
     * Section 1: University Programs Table (5-10 actual degree programs)
     * Section 2: Additional Funding Opportunities (external fellowships if found)
     * Section 3: Personalized guidance with trade-offs and next steps

6. FOLLOW-UP GENERATOR (Gemini API)
   ↓
   - Analyzes: profile + query type + results
   - Generates 3 contextual questions:
     * "Compare Carnegie Mellon and Cedars-Sinai programs?"
     * "Search for programs with later deadlines?"
     * "Learn about GRE waiver options?"

7. OUTPUT TO USER
   ↓
   Complete response with table + guidance + follow-ups
```

---

## Key Design Decisions

### 1. **Two-Stage Information Gathering**
- **Coordinator** extracts and saves info immediately (even when asking questions)
- **Planner** refines and validates profile before search
- **Result**: No information loss, efficient multi-turn conversations

### 2. **Flexible Search Query Generation**
- Learned from iterations: avoid over-constraining
- Simple, effective queries work better than complex ones
- Multiple angles: funding, field, degree, location

### 3. **Session-Based Memory**
- Each chat session = independent profile
- Supports multiple use cases (different students, scenarios)
- Clean separation of concerns

### 4. **Intelligent Follow-ups**
- Context-aware suggestions
- Guides exploration naturally
- Reduces "what do I ask next?" friction

---

## Scalability & Future Enhancements

### Current Limitations
- In-memory storage (lost on restart)
- No persistent chat history across browser sessions
- Rate limited by API quotas

### Potential Improvements
1. **Persistent Storage**: Database for profiles and chat history
2. **Vector Store**: Semantic search over past conversations
3. **Caching**: Cache search results to reduce API calls
4. **Batch Processing**: Process multiple searches in parallel
5. **Advanced Filtering**: ML-based program matching
6. **User Accounts**: Save preferences, favorites, application tracking
7. **Email Integration**: Deadline reminders, application status updates
8. **Document Analysis**: Parse program websites directly

---

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| LLM | Google Gemini 2.0 Flash | Planning, reasoning, synthesis |
| Web Search | Serper API | Real-time program discovery |
| UI Framework | Streamlit | Web interface |
| Memory | Python in-memory dict | Profile storage |
| Session Management | Streamlit session_state | Chat history |
| Language | Python 3.13 | Core implementation |
| Deployment | ADK Playground ready | Production deployment |

---

## Conclusion

GradPath's architecture demonstrates:
- **Agentic Design**: Autonomous decision-making and task breakdown
- **User-Centric**: Multi-session support, intelligent follow-ups
- **Robust**: Error handling, fallbacks, logging
- **Scalable**: Modular design, clear separation of concerns
- **Production-Ready**: ADK compatible, comprehensive features

The system successfully combines modern LLM capabilities with traditional search tools to create a helpful, conversational assistant for graduate school search.  


# GradPath - Adaptive Agentic Search Assistant

**An intelligent graduate program search assistant powered by Google Gemini and multi-agent reasoning.**

GradPath transforms the overwhelming graduate school search process into a personalized, conversational experience. Unlike traditional search engines that treat everyone the same, GradPath builds a persistent memory profile, adapts its search strategies based on your needs, and provides comprehensive guidance through an intelligent multi-agent system.

## 🎯 Key Features

- **Intelligent Conversation**: Coordinator agent extracts information naturally from conversation
- **Persistent Memory**: Remembers your GPA, preferences, and requirements across the entire session
- **Adaptive Search**: Multi-agent pipeline plans optimal search strategies based on your profile
- **Deep Dive & Compare**: Get detailed info on specific programs or side-by-side comparisons
- **Multi-Session Support**: Manage multiple independent searches with preserved history
- **Follow-up Questions**: System suggests intelligent next steps to guide exploration


## 🏗️ Architecture Overview

GradPath uses a sophisticated multi-agent pipeline:

```
User Input → Coordinator → Classifier → Planner → Search Executor → Writer → Follow-up Generator
                ↓                                        ↓
            Memory Store                           Serper API
```

**Agent Roles**:
1. **Coordinator**: Analyzes intent, extracts profile info, determines readiness
2. **Classifier**: Routes to new_search, deep_dive, or comparison handlers
3. **Planner**: Creates optimized search strategies with 3-5 queries
4. **Search Executor**: Executes web searches via Serper API with rate limiting
5. **Writer**: Synthesizes results into personalized recommendations
6. **Follow-up Generator**: Suggests intelligent next questions

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Google Gemini API key ([From  here](https://aistudio.google.com/app/apikey))
- Serper API key ([From here](https://serper.dev))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Desae/aseda-addai-deseh.git
cd aseda-addai-deseh
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

5. **Run the application**
```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 💡 Usage Examples

### Example 1: Basic Search
```
You: "I have a 3.4 GPA and want a fully funded MS in Data Science in the US or Canada. 
      I prefer programs that don't require the GRE."

GradPath: [Extracts: GPA=3.4, field=Data Science, degree=MS, location=US/Canada, 
           funding=fully funded, GRE=not required]
          [Plans 4 optimized searches]
          [Returns personalized recommendations with funding details]
```

### Example 2: Deep Dive
```
You: "Tell me more about Stanford's Data Science program"

GradPath: [Provides detailed breakdown]
          - Program Overview
          - Admission Requirements  
          - Funding Options
          - Application Details
          - Unique Features
          - References with links
```

### Example 3: Comparison
```
You: "Compare MIT and CMU for Data Science"

GradPath: [Creates side-by-side comparison table]
          - Admission requirements
          - Funding opportunities
          - Program structure
          - Application deadlines
          - Recommendations based on your profile
```

---

## � Project Structure

```
aseda-addai-deseh/
├── src/
│   ├── config.py              # API keys and configuration
│   ├── executor.py            # Main agentic pipeline orchestration
│   ├── planner.py             # Search strategy planning
│   ├── memory.py              # Student profile storage
│   ├── root_agent.py          # Entry point for ADK Playground
│   └── tools/
│       └── search.py          # Serper API integration
├── streamlit_app.py           # Multi-session Streamlit UI
├── requirements.txt           # Python dependencies
├── .env                       # API keys (create this)
├── ARCHITECTURE.md            # Detailed system design
├── EXPLANATION.md             # Technical explanation
├── DEMO.md                    # Demo video guide
└── README.md                  # This file
```

---

## 🎬 Demo Video

📺 **[Watch the demo here](https://your.video.link.here)**

See [DEMO.md](DEMO.md) for a detailed recording guide and script.

---

## 📚 Documentation


## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Complete system architecture with diagrams, component breakdowns, and data flows
- **[EXPLANATION.md](EXPLANATION.md)**: Technical explanation of agent workflow, modules, tools, and design decisions
- **[DEMO.md](DEMO.md)**: Demo video recording timestamps and scripts

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|------------|
| **LLM** | Google Gemini 2.0 Flash (gemini-2.0-flash) |
| **Web Search** | Serper API (Google Search) |
| **UI Framework** | Streamlit |
| **Memory** | In-memory session-based profiles |
| **Language** | Python 3.10+ |
| **Validation** | Pydantic |

---

## 🧪 Testing

Run the test script to verify setup:
```bash
bash TEST.sh
```

Or test manually:
```bash
# 1. Verify environment variables
python -c "from src.config import GEMINI_API_KEY, SERPER_API_KEY; print('✅ API keys loaded')"

# 2. Test Gemini connection
python -c "import google.generativeai as genai; from src.config import GEMINI_API_KEY; genai.configure(api_key=GEMINI_API_KEY); print('✅ Gemini connected')"

# 3. Test Serper API
python -c "from src.tools.search import serper_program_search; print('✅ Serper working')"

# 4. Run the app
streamlit run streamlit_app.py
```

---

## 🎯 Key Agentic Features

### 1. **Intelligent Planning**
- Coordinator analyzes queries before acting
- Planner generates optimized search strategies
- Query classifier routes to appropriate handlers

### 2. **Tool Orchestration**
- Multiple Serper API calls per request
- Rate limiting (0.5s delays)
- Result deduplication and synthesis

### 3. **Persistent Memory**
- Session-based student profiles
- Information extracted from natural language
- Memory persists across conversation turns
- Independent profiles per chat session

### 4. **Adaptive Behavior**
- Different handlers for different query types
- Personalized search queries based on profile
- Follow-up questions guide exploration

---

## 🔍 How It Works

1. **User Input**: "I want a fully funded MS in AI in the US with a 3.5 GPA"

2. **Coordinator**: 
   - Extracts: field=AI, degree=MS, location=US, GPA=3.5, funding=full
   - Saves to memory immediately
   - Determines: ready to search ✅

3. **Classifier**: Identifies as "new_search"

4. **Planner**: 
   - Reviews profile: AI, MS, US, 3.5 GPA, full funding
   - Generates queries:
     - "MS Artificial Intelligence fully funded USA"
     - "AI graduate programs scholarships 3.5 GPA"
     - "Master AI funding TA RA USA"

5. **Search Executor**: 
   - Executes 3 Serper API calls
   - Collects 15-20 program candidates
   - Rate limits appropriately

6. **Writer**: 
   - Synthesizes top 5-10 programs
   - Creates markdown table with details
   - Adds personalized guidance
   - Includes source links

7. **Follow-up Generator**:
   - Suggests: "Would you like to compare Stanford vs MIT's programs?"
   - Or: "Should I look for programs with later deadlines?"

---

## 🌟 Advanced Features

### Deep Dive
Ask for details about a specific university:
- "Tell me more about Stanford"
- "What are CMU's admission requirements?"

System performs focused research on that program with 3-5 targeted searches.

### Comparison
Compare multiple universities side-by-side:
- "Compare MIT and Stanford"
- "What's the difference between CMU and Berkeley?"

System creates comparison tables with parallel research.

### Multi-Session Chat
- Create multiple independent search threads
- Switch between sessions without losing context
- Each session maintains its own memory profile

---

## 🚧 Known Limitations

1. **Memory Persistence**: In-memory only (lost on restart)
   - *Future*: Add Redis or PostgreSQL

2. **API Rate Limits**: Serper API has monthly quotas on free tier
   - *Mitigation*: 0.5s delays, query optimization

3. **Real-time Accuracy**: Graduate program info changes frequently
   - *Recommendation*: Verify details with official sources

4. **Search Specificity**: Overly complex queries may return few results
   - *Mitigation*: Planner generates simple, natural queries

---

## 🤝 Contributing

This is a hackathon submission project. For questions or feedback:
- Open an issue on GitHub
- Contact: aseda.oad@gmail.com

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏆 Hackathon Submission

### Judging Criteria Alignment

| Criterion | How GradPath Addresses It |
|-----------|---------------------------|
| **Technical Excellence** | Clean architecture, robust error handling, comprehensive testing, production-ready code |
| **Solution Architecture** | Multi-agent pipeline, clear separation of concerns, detailed documentation, well-organized codebase |
| **Innovative Gemini Integration** | 6 specialized Gemini agents, creative prompt engineering, JSON-structured reasoning |
| **Societal Impact** | Solves real problem (graduate school search), accessible to all students, reduces information overload |

### Submission Checklist

- ✅ All code in `src/` runs without errors
- ✅ `ARCHITECTURE.md` contains detailed diagrams and explanations
- ✅ `EXPLANATION.md` covers workflow, modules, tools, and limitations
- ✅ `DEMO.md` with video link and timestamped guide
- ✅ Clean, documented, production-ready code
- ✅ Multi-agent agentic behavior demonstrated
- ✅ Persistent memory with session management
- ✅ Real-world tool integration (Serper API)

---

## 🙏 Acknowledgments

- **Google Gemini API**: Powers all agent reasoning and synthesis
- **Serper API**: Provides real-time web search results
- **Streamlit**: Enables rapid UI development
- **Hackathon Organizers**: For the opportunity to build this project

---

**Built with ❤️ for the Agentic AI App Hackathon**



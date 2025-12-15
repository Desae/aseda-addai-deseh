# GradPath Demo Video Guide

## 📺 Demo Video Link

**Hosted Video Link (YouTube Unlisted / Loom):**  
> 🔗 **[INSERT YOUR VIDEO LINK HERE]**

---

## ⏱️ Demo Script

### **00:00–00:30 — Introduction & Setup**

**Canva Screen**

Hi, my name is Aseda Addai-Deseh and I'm demonstrating GradPath - an intelligent graduate program search assistant powered by the Google Gemini API.

**Show Streamlit Startup page**

GradPath transforms the overwhelming graduate school search process into a personalized, conversational experience. Unlike traditional search engines that treat everyone the same, GradPath builds a persistent memory profile, adapts its search strategies based on your needs, and provides comprehensive guidance through an intelligent multi-agent system.

The frontend is built with Streamlit, making it easy to interact with. 

**Show terminal**

To start it up, I simply run: `streamlit run streamlit_app.py`

---

### **00:30–01:30 — User Input → Planning Step**

**App screen**

When I enter my query: 'I'm interested in PhD programs in Machine Learning in the US, with a focus on healthcare with full funding for the Fall 2026 intake. My GPA is 3.7.' - watch what happens.

**Terminal**

The Coordinator agent analyzes my intent and extracts my profile information - GPA of 3.7, field is Machine Learning, degree level is PhD, preferred country is US, focus on healthcare applications, full funding requirement, and Fall 2026 intake. Notice how the sidebar updates to show this information.

The Classifier agent routed this query to the appropriate handler. Since this is a new search request, it routes to the new_search handler.

Finally, the Planner agent creates an optimized search strategy, generating a number of targeted queries that search from different angles - across program pages, funding opportunities, and for the specific domain, in this case for healthcare AI research programs.

All of this happens seamlessly, with the system building a persistent memory profile as we go.

---

### **01:30–02:30 — Tool Calls & Memory Retrieval**

**Terminal - search tool**

Now the Search Executor performs multiple web searches using the Serper API. Each query targets different universities and program aspects. It searches for 'PhD Machine Learning healthcare USA fully funded', then 'Machine Learning healthcare AI PhD programs', and synthesizes results from multiple sources including universities like Harvard, and CMU.

**Streamlit app - memory tool**

Here's a key agentic feature - persistent memory. When I simply ask 'What about Germany?', notice it doesn't ask for my GPA, field, or degree level again. The system remembers my GPA of 3.7, my interest in Machine Learning with healthcare focus, that I want a PhD with full funding for Fall 2026. It intelligently updates just the location preference from US to Germany and refines the search accordingly.

You can see in the sidebar that the profile now shows 'preferred_countries: Germany' while keeping all my other preferences intact. This is true conversational AI with persistent memory!

---

### **02:30–03:30 — Final Output & Edge-Case Handling**

**Streamlit app**

The Writer agent, powered by Google Gemini, synthesizes everything into a formatted response. Notice the table with program names, universities, funding info, and direct links. Below that, personalized guidance explains why each program fits my profile.

The agent also suggests follow-up questions. Now let me demonstrate the comparison feature by asking: 'Compare Carnegie Mellon University and Cedars-Sinai programs'.

**Quick Terminal view + Streamlit app**

The Classifier agent recognizes this as a comparison query and routes it to the comparison handler. It creates a side-by-side comparison table showing focus areas, funding options, curriculum, and research opportunities. Notice it still remembers we're looking at Machine Learning with healthcare focus - that's the persistent memory at work again!

**Deep Dive demo**

Now watch this - when I ask 'Tell me more about Cedars-Sinai's program', the Classifier recognizes this as a deep_dive query and routes it to the deep dive handler.

The system performs a number of focused searches specifically about Cedars-Sinai's Machine Learning program - looking at their admission requirements, faculty research, funding opportunities, and healthcare AI initiatives.

Notice it generates a comprehensive breakdown with sections on Program Overview, Admission Requirements, Funding Options, Application Details, and Unique Features - all with actual website links as references. And again, it still remembers my GPA of 3.7, my healthcare focus, and all my other preferences!

---

### **03:30–04:00 — Wrap-up (Optional)**

**Streamlit app screen**

Finally, GradPath supports multiple independent chat sessions. I can start a new chat for a different search, and return to this one anytime with all context preserved.

**Add search in new chat:**
> I'm looking for MS programs in Agriculture in Australia that waive the GRE

**Then return to show old chat**

**End**

**Streamlit app scrolling through old chats**

To summarize: GradPath demonstrates true agentic AI with intelligent planning powered by Google Gemini API, dynamic tool use via Serper API, persistent memory management that remembers your preferences across questions, and adaptive conversation handling. It condenses weeks or months of overwhelming grad school research into a smooth, personalized search experience that takes just minutes.

Once again, my name is Aseda Addai-Deseh and thank you for your attention.

---
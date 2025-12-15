"""
Streamlit UI for GradPath - Graduate Program Search Assistant
With Multi-Session Chat History Management
"""

import streamlit as st
import uuid
from datetime import datetime
from src.root_agent import handle_message
from src.memory import profile_store

# Page configuration
st.set_page_config(
    page_title="GradPath - Your Grad School Guide",
    page_icon="🎓",
    layout="wide"
)

# Initialize session storage for chat history
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_session_id" not in st.session_state:
    # Create first session
    first_session_id = str(uuid.uuid4())
    st.session_state.current_session_id = first_session_id
    st.session_state.chat_sessions[first_session_id] = {
        "id": first_session_id,
        "title": "New Chat",
        "created_at": datetime.now().isoformat(),
        "messages": [{
            "role": "assistant",
            "content": """Welcome to GradPath! 👋

I'm here to help you find the perfect graduate program. Tell me about:
- Your academic background (GPA, test scores)
- Field of study and degree level (MS/PhD)
- Preferred countries or cities
- Funding requirements
- Any other preferences (GRE waiver, specific intake terms, etc.)

What graduate programs are you looking for?"""
        }]
    }

# Helper functions for session management
def create_new_session():
    """Create a new chat session"""
    new_session_id = str(uuid.uuid4())
    st.session_state.chat_sessions[new_session_id] = {
        "id": new_session_id,
        "title": "New Chat",
        "created_at": datetime.now().isoformat(),
        "messages": [{
            "role": "assistant",
            "content": """Welcome to GradPath! 👋

I'm here to help you find the perfect graduate program. Tell me about:
- Your academic background (GPA, test scores)
- Field of study and degree level (MS/PhD)
- Preferred countries or cities
- Funding requirements
- Any other preferences (GRE waiver, specific intake terms, etc.)

What graduate programs are you looking for?"""
        }]
    }
    st.session_state.current_session_id = new_session_id
    return new_session_id

def switch_session(session_id):
    """Switch to a different chat session"""
    st.session_state.current_session_id = session_id

def delete_session(session_id):
    """Delete a chat session"""
    if len(st.session_state.chat_sessions) > 1:
        del st.session_state.chat_sessions[session_id]
        # Clean up profile data
        profile_store._profiles.pop(session_id, None)
        # Switch to most recent session
        remaining_sessions = sorted(
            st.session_state.chat_sessions.items(),
            key=lambda x: x[1]["created_at"],
            reverse=True
        )
        st.session_state.current_session_id = remaining_sessions[0][0]
    else:
        st.warning("Cannot delete the last chat session!")

def update_session_title(session_id, messages):
    """Auto-generate session title from first user message"""
    session = st.session_state.chat_sessions[session_id]
    if session["title"] == "New Chat" and len(messages) > 1:
        # Find first user message
        for msg in messages:
            if msg["role"] == "user":
                # Use first 40 chars of first user message as title
                title = msg["content"][:40]
                if len(msg["content"]) > 40:
                    title += "..."
                session["title"] = title
                break

def get_current_session():
    """Get current session data"""
    return st.session_state.chat_sessions[st.session_state.current_session_id]

# Title and description
st.title("🎓 GradPath")
st.markdown("### Your AI-Powered Graduate Program Search Assistant")
st.markdown("Find fully funded MS/PhD programs tailored to your profile!")

# Sidebar for session management
with st.sidebar:
    st.header("💬 Chat Sessions")
    
    # New Chat button (prominent)
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        create_new_session()
        st.rerun()
    
    st.markdown("---")
    
    # Display all chat sessions
    current_session_id = st.session_state.current_session_id
    sessions_sorted = sorted(
        st.session_state.chat_sessions.items(),
        key=lambda x: x[1]["created_at"],
        reverse=True
    )
    
    st.subheader("Your Chats")
    for session_id, session_data in sessions_sorted:
        is_current = session_id == current_session_id
        
        # Create container for each session
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Session button with indicator for current session
            button_label = f"{'🔵' if is_current else '⚪'} {session_data['title']}"
            if st.button(button_label, key=f"session_{session_id}", use_container_width=True):
                if not is_current:
                    switch_session(session_id)
                    st.rerun()
        
        with col2:
            # Delete button (only show if not current or if multiple sessions exist)
            if len(st.session_state.chat_sessions) > 1:
                if st.button("🗑️", key=f"delete_{session_id}"):
                    delete_session(session_id)
                    st.rerun()
    
    st.markdown("---")
    
    # Current session info
    current_session = get_current_session()
    st.caption(f"Session: {current_session_id[:8]}...")
    st.caption(f"Messages: {len(current_session['messages'])}")
    
    # Display current profile with refresh button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Your Profile")
    with col2:
        if st.button("🔄", key="refresh_profile", help="Refresh profile data"):
            st.rerun()
    
    profile = profile_store.as_dict(current_session_id)
    if profile:
        for key, value in profile.items():
            if value:
                st.text(f"{key}: {value}")
    else:
        st.text("No profile data yet")
    
    st.markdown("---")
    st.markdown("""
    **How to use:**
    1. Tell me about your background
    2. Specify your preferences
    3. Get personalized recommendations!
    4. Start new chats for different searches
    """)

# Get current session messages
current_session = get_current_session()
current_messages = current_session["messages"]

# Display chat history for current session
for message in current_messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        st.markdown(content, unsafe_allow_html=False)

# Chat input
if prompt := st.chat_input("Tell me about your graduate school preferences..."):
    # Add user message to current session
    current_messages.append({"role": "user", "content": prompt})
    
    # Update session title if this is the first user message
    update_session_title(st.session_state.current_session_id, current_messages)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Searching for programs..."):
            try:
                response = handle_message(prompt, st.session_state.current_session_id)
                
                # Check if response contains a markdown table
                if "|" in response and "---" in response:
                    # Split response into parts
                    parts = response.split("\n\n")
                    
                    for part in parts:
                        if "|" in part and "---" in part:
                            # This is a table - render it properly
                            st.markdown(part)
                        elif part.strip().startswith("#"):
                            # This is a heading
                            st.markdown(part)
                        elif part.strip().startswith("*") or part.strip().startswith("-"):
                            # This is a list
                            st.markdown(part)
                        elif part.strip():
                            # Regular text
                            st.markdown(part)
                else:
                    # No table, just render as markdown
                    st.markdown(response)
                
                # Add assistant response to current session
                current_messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"⚠️ An error occurred: {str(e)}"
                st.error(error_msg)
                current_messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Powered by Google Gemini & Serper API | 💾 Chat history preserved across sessions</div>",
    unsafe_allow_html=True
)

"""
Streamlit web interface for the Customer Support Desk.
Provides a modern, user-friendly interface for customer interactions.
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time
from typing import Dict, Any, Optional

# Page configuration
st.set_page_config(
    page_title="Customer Support Desk",
    page_icon="🛟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .response-box {
        background-color: #e8f4fd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .emergency-box {
        background-color: #f8d7da;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #dc3545;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-active {
        background-color: #28a745;
    }
    .status-inactive {
        background-color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'customer_id' not in st.session_state:
    st.session_state.customer_id = f"customer_{int(time.time())}"

# Configuration
API_BASE_URL = "http://localhost:8000"
API_TOKEN = "your-api-token-here"  # In production, use proper authentication

def make_api_request(endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Make API request to the customer support backend.
    
    Args:
        endpoint: API endpoint
        data: Request data
        
    Returns:
        API response or None if error
    """
    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def get_crew_status() -> Optional[Dict[str, Any]]:
    """Get the current status of all agents."""
    try:
        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        response = requests.get(f"{API_BASE_URL}/support/status", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except requests.exceptions.RequestException:
        return None

def classify_request(user_input: str) -> str:
    """
    Classify user request to determine appropriate agent.
    
    Args:
        user_input: User's message
        
    Returns:
        Agent type: "billing", "technical", "escalation", or "general"
    """
    user_input_lower = user_input.lower()
    
    # Billing keywords
    billing_keywords = [
        "payment", "charge", "billing", "invoice", "bill", "refund",
        "credit", "subscription", "plan", "renewal", "cost", "price"
    ]
    
    # Technical keywords
    technical_keywords = [
        "install", "setup", "configure", "error", "bug", "crash",
        "not working", "broken", "issue", "problem", "troubleshoot",
        "slow", "performance", "lag", "network", "connection"
    ]
    
    # Escalation keywords
    escalation_keywords = [
        "complaint", "dissatisfied", "unhappy", "angry", "frustrated",
        "escalate", "manager", "supervisor", "compensation", "emergency"
    ]
    
    # Count matches
    billing_score = sum(1 for keyword in billing_keywords if keyword in user_input_lower)
    technical_score = sum(1 for keyword in technical_keywords if keyword in user_input_lower)
    escalation_score = sum(1 for keyword in escalation_keywords if keyword in user_input_lower)
    
    if escalation_score > 0:
        return "escalation"
    elif billing_score > technical_score:
        return "billing"
    elif technical_score > 0:
        return "technical"
    else:
        return "general"

def display_agent_status():
    """Display the status of all agents."""
    st.sidebar.markdown("### Agent Status")
    
    status = get_crew_status()
    if status:
        agents = status.get("agents", {})
        
        for agent_name, agent_info in agents.items():
            status_color = "status-active" if agent_info.get("interaction_count", 0) > 0 else "status-inactive"
            status_text = "Active" if agent_info.get("interaction_count", 0) > 0 else "Inactive"
            
            st.sidebar.markdown(f"""
            <div class="agent-card">
                <span class="status-indicator {status_color}"></span>
                <strong>{agent_name}</strong><br>
                Status: {status_text}<br>
                Interactions: {agent_info.get("interaction_count", 0)}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.warning("Unable to fetch agent status")

def main():
    """Main application function."""
    # Header
    st.markdown('<h1 class="main-header">🛟 Customer Support Desk</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("### Customer Information")
    st.session_state.customer_id = st.sidebar.text_input(
        "Customer ID", 
        value=st.session_state.customer_id,
        help="Enter your customer ID for tracking"
    )
    
    # Display agent status
    display_agent_status()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### How can we help you today?")
        
        # Request type selection
        request_type = st.selectbox(
            "Select your request type:",
            ["Auto-detect", "Billing & Payments", "Technical Support", "Escalation & Complaints", "General Inquiry"]
        )
        
        # Emergency toggle
        emergency = st.checkbox("🚨 This is an emergency", help="Check this for urgent situations")
        
        # Message input
        user_message = st.text_area(
            "Describe your issue:",
            height=150,
            placeholder="Please describe your issue in detail..."
        )
        
        # Submit button
        if st.button("Send Message", type="primary"):
            if user_message.strip():
                process_user_request(user_message, request_type, emergency)
            else:
                st.warning("Please enter a message before sending.")
    
    with col2:
        st.markdown("### Quick Actions")
        
        # Quick action buttons
        if st.button("📞 Contact Human Agent"):
            st.info("Connecting you to a human agent...")
            st.session_state.chat_history.append({
                "user": "System",
                "message": "Connecting to human agent...",
                "timestamp": datetime.now().strftime("%H:%M"),
                "agent_type": "human"
            })
        
        if st.button("📋 View Chat History"):
            display_chat_history()
        
        if st.button("🔄 Refresh Status"):
            st.rerun()
        
        # Information panel
        st.markdown("### Support Information")
        st.markdown("""
        **Available Support:**
        - 💳 Billing & Payment Issues
        - 🔧 Technical Problems
        - 📞 Escalations & Complaints
        - ❓ General Inquiries
        
        **Response Time:**
        - General: 2-4 hours
        - Urgent: 15-30 minutes
        - Emergency: Immediate
        """)

def process_user_request(user_message: str, request_type: str, emergency: bool):
    """Process user request and get response from appropriate agent."""
    
    # Add user message to chat history
    st.session_state.chat_history.append({
        "user": "Customer",
        "message": user_message,
        "timestamp": datetime.now().strftime("%H:%M"),
        "agent_type": "customer"
    })
    
    # Prepare request data
    request_data = {
        "message": user_message,
        "customer_id": st.session_state.customer_id,
        "emergency": emergency,
        "context": {
            "request_type": request_type,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # Determine endpoint based on request type
    if request_type == "Auto-detect":
        endpoint = "/support/request"
    elif request_type == "Billing & Payments":
        endpoint = "/support/billing"
    elif request_type == "Technical Support":
        endpoint = "/support/technical"
    elif request_type == "Escalation & Complaints":
        endpoint = "/support/escalation"
    else:
        endpoint = "/support/request"
    
    # Show processing message
    with st.spinner("Processing your request..."):
        response = make_api_request(endpoint, request_data)
    
    if response:
        # Add agent response to chat history
        st.session_state.chat_history.append({
            "user": "Support Agent",
            "message": response.get("response", "No response available"),
            "timestamp": datetime.now().strftime("%H:%M"),
            "agent_type": response.get("agent_type", "unknown")
        })
        
        # Display response
        display_response(response)
    else:
        st.error("Unable to process your request. Please try again or contact support directly.")

def display_response(response: Dict[str, Any]):
    """Display the agent's response."""
    agent_type = response.get("agent_type", "unknown")
    message = response.get("response", "No response available")
    
    # Determine response styling based on agent type
    if agent_type == "escalation":
        st.markdown(f"""
        <div class="emergency-box">
            <strong>🚨 Escalation Specialist Response:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="response-box">
            <strong>💬 {agent_type.title()} Agent Response:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)

def display_chat_history():
    """Display the chat history."""
    st.markdown("### Chat History")
    
    if not st.session_state.chat_history:
        st.info("No chat history available.")
        return
    
    for entry in st.session_state.chat_history:
        if entry["user"] == "Customer":
            st.markdown(f"""
            <div style="text-align: right; margin: 10px 0;">
                <strong>You ({entry['timestamp']}):</strong><br>
                {entry['message']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: left; margin: 10px 0;">
                <strong>{entry['user']} ({entry['timestamp']}):</strong><br>
                {entry['message']}
            </div>
            """, unsafe_allow_html=True)

# Run the application
if __name__ == "__main__":
    main() 
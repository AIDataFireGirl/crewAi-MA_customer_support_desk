"""
Customer Support Crew using CrewAI framework.
Orchestrates multiple specialized agents for comprehensive customer support.
"""

from typing import Dict, Any, Optional, List
from crewai import Crew, Process
from agents.billing_agent import BillingAgent
from agents.tech_support_agent import TechSupportAgent
from agents.escalation_agent import EscalationAgent
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomerSupportCrew:
    """Main crew class that orchestrates customer support agents."""
    
    def __init__(self):
        """Initialize the customer support crew with all specialized agents."""
        self.billing_agent = BillingAgent()
        self.tech_support_agent = TechSupportAgent()
        self.escalation_agent = EscalationAgent()
        
        # Initialize the crew with all agents
        self.crew = self._create_crew()
        
        logger.info("Customer Support Crew initialized successfully")
    
    def _create_crew(self) -> Crew:
        """Create the CrewAI crew with all specialized agents."""
        try:
            crew = Crew(
                agents=[
                    self.billing_agent.agent,
                    self.tech_support_agent.agent,
                    self.escalation_agent.agent
                ],
                tasks=[],  # Tasks will be created dynamically
                process=Process.sequential,  # Process tasks sequentially for better control
                verbose=True,
                memory=True
            )
            
            logger.info("CrewAI crew created successfully with all agents")
            return crew
            
        except Exception as e:
            logger.error(f"Failed to create crew: {e}")
            raise
    
    def route_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Route customer request to the appropriate specialized agent.
        
        Args:
            user_input: Customer's request or inquiry
            context: Additional context about the customer and situation
            
        Returns:
            Response from the appropriate specialized agent
        """
        try:
            # Security: Validate input
            if not user_input or not user_input.strip():
                return "I'm sorry, but I couldn't process your request. Please provide a valid message."
            
            # Determine the appropriate agent based on request content
            agent_type = self._classify_request(user_input)
            
            # Route to appropriate agent
            if agent_type == "billing":
                return self.billing_agent.process_request(user_input, context)
            elif agent_type == "technical":
                return self.tech_support_agent.process_request(user_input, context)
            elif agent_type == "escalation":
                return self.escalation_agent.process_request(user_input, context)
            else:
                # Default to general support with escalation capability
                return self._handle_general_request(user_input, context)
                
        except Exception as e:
            logger.error(f"Error routing request: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again or contact our support team directly."
    
    def _classify_request(self, user_input: str) -> str:
        """
        Classify the customer request to determine the appropriate agent.
        
        Args:
            user_input: Customer's request
            
        Returns:
            Agent type: "billing", "technical", "escalation", or "general"
        """
        user_input_lower = user_input.lower()
        
        # Billing-related keywords
        billing_keywords = [
            "payment", "charge", "billing", "invoice", "bill", "refund",
            "credit", "subscription", "plan", "renewal", "cost", "price",
            "fee", "charge", "charged", "payment method", "credit card"
        ]
        
        # Technical support keywords
        technical_keywords = [
            "install", "setup", "configure", "error", "bug", "crash",
            "not working", "broken", "issue", "problem", "troubleshoot",
            "slow", "performance", "lag", "network", "connection",
            "internet", "login", "password", "access", "feature",
            "how to", "guide", "tutorial", "help", "support"
        ]
        
        # Escalation keywords
        escalation_keywords = [
            "complaint", "dissatisfied", "unhappy", "angry", "frustrated",
            "escalate", "manager", "supervisor", "higher authority",
            "compensation", "refund", "credit", "policy", "rule",
            "procedure", "service", "quality", "failure", "emergency",
            "urgent", "crisis", "immediate", "critical", "legal",
            "lawyer", "police", "threat", "danger", "harm"
        ]
        
        # Count keyword matches for each category
        billing_score = sum(1 for keyword in billing_keywords if keyword in user_input_lower)
        technical_score = sum(1 for keyword in technical_keywords if keyword in user_input_lower)
        escalation_score = sum(1 for keyword in escalation_keywords if keyword in user_input_lower)
        
        # Determine the most appropriate agent
        if escalation_score > 0:
            return "escalation"
        elif billing_score > technical_score:
            return "billing"
        elif technical_score > 0:
            return "technical"
        else:
            return "general"
    
    def _handle_general_request(self, user_input: str, 
                               context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle general requests that don't clearly fit a specific category.
        
        Args:
            user_input: Customer's general request
            context: Additional context
            
        Returns:
            General support response with routing options
        """
        return f"""
        Thank you for contacting our customer support team. I'm here to help you with your inquiry.

        **How I Can Help:**
        Based on your message, I can assist you with several areas:

        **Billing & Payments:**
        - Payment issues and charges
        - Invoice and billing questions
        - Refunds and credits
        - Subscription management

        **Technical Support:**
        - Software installation and setup
        - Error troubleshooting
        - Performance optimization
        - Feature guidance and tutorials

        **Escalation & Complaints:**
        - Complex issues requiring escalation
        - Complaints and dissatisfaction
        - Policy disputes
        - Compensation requests

        **Next Steps:**
        Please provide more specific details about your concern, and I'll route you to the appropriate specialist who can best assist you.

        **For Immediate Assistance:**
        - Billing: billing@company.com
        - Technical Support: tech-support@company.com
        - Escalations: escalations@company.com

        What specific issue would you like help with today?
        """
    
    def process_complex_request(self, user_input: str, 
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process complex requests that may require multiple agents.
        
        Args:
            user_input: Customer's complex request
            context: Additional context
            
        Returns:
            Comprehensive response with multiple agent inputs
        """
        try:
            # Create tasks for each agent to contribute
            tasks = self._create_multi_agent_tasks(user_input, context)
            
            # Execute the crew with multiple tasks
            result = self.crew.kickoff()
            
            # Compile comprehensive response
            comprehensive_response = self._compile_multi_agent_response(result, context)
            
            logger.info("Complex request processed successfully with multiple agents")
            return comprehensive_response
            
        except Exception as e:
            logger.error(f"Error processing complex request: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your complex request. Please contact our support team directly.",
                "agents_involved": [],
                "escalation_required": True
            }
    
    def _create_multi_agent_tasks(self, user_input: str, 
                                 context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Create tasks for multiple agents to handle complex requests.
        
        Args:
            user_input: Customer's complex request
            context: Additional context
            
        Returns:
            List of tasks for different agents
        """
        tasks = []
        
        # Task for billing agent
        billing_task = {
            "agent": self.billing_agent.agent,
            "task": f"Analyze the billing aspects of this request: {user_input}",
            "context": context
        }
        tasks.append(billing_task)
        
        # Task for technical support agent
        tech_task = {
            "agent": self.tech_support_agent.agent,
            "task": f"Analyze the technical aspects of this request: {user_input}",
            "context": context
        }
        tasks.append(tech_task)
        
        # Task for escalation agent
        escalation_task = {
            "agent": self.escalation_agent.agent,
            "task": f"Analyze the escalation aspects of this request: {user_input}",
            "context": context
        }
        tasks.append(escalation_task)
        
        return tasks
    
    def _compile_multi_agent_response(self, crew_result: Any, 
                                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compile responses from multiple agents into a comprehensive response.
        
        Args:
            crew_result: Result from crew execution
            context: Additional context
            
        Returns:
            Comprehensive response with all agent inputs
        """
        return {
            "response": crew_result,
            "agents_involved": ["billing", "technical", "escalation"],
            "timestamp": datetime.now().isoformat(),
            "escalation_required": False,
            "context": context
        }
    
    def get_crew_status(self) -> Dict[str, Any]:
        """Get the current status of all agents in the crew."""
        return {
            "crew_status": "active",
            "agents": {
                "billing": self.billing_agent.get_agent_info(),
                "technical": self.tech_support_agent.get_agent_info(),
                "escalation": self.escalation_agent.get_agent_info()
            },
            "total_interactions": sum([
                self.billing_agent.get_agent_info()["interaction_count"],
                self.tech_support_agent.get_agent_info()["interaction_count"],
                self.escalation_agent.get_agent_info()["interaction_count"]
            ]),
            "last_updated": datetime.now().isoformat()
        }
    
    def handle_emergency(self, user_input: str, 
                        context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle emergency situations with immediate escalation.
        
        Args:
            user_input: Customer's emergency request
            context: Additional context
            
        Returns:
            Immediate emergency response
        """
        logger.warning(f"Emergency situation detected: {user_input}")
        
        # Immediately route to escalation agent
        emergency_response = self.escalation_agent.process_request(user_input, context)
        
        # Log emergency for monitoring
        logger.critical(f"Emergency handled for customer: {context.get('customer_id', 'unknown') if context else 'unknown'}")
        
        return emergency_response 
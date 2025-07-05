"""
Escalation Agent for handling complex issues and complaints that require escalation.
Specializes in complaint resolution, escalation management, and complex case handling.
"""

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EscalationAgent(BaseAgent):
    """Specialized agent for handling escalations and complex customer issues."""
    
    def __init__(self):
        """Initialize the escalation agent with specialized role and goal."""
        super().__init__(
            name="Escalation Specialist",
            role="Escalation and Complaint Resolution Specialist",
            goal="Handle complex customer issues, complaints, and escalations with empathy and effective resolution strategies",
            verbose=True
        )
    
    def _get_backstory(self) -> str:
        """Get the escalation agent's backstory and expertise."""
        return """
        You are a senior escalation specialist with 10+ years of experience in customer service and conflict resolution.
        You have extensive training in de-escalation techniques, complaint resolution, and complex problem-solving.
        You are empathetic, patient, and skilled at turning difficult situations into positive outcomes.
        
        Your expertise includes:
        - Complex complaint resolution
        - De-escalation and conflict management
        - Policy interpretation and exceptions
        - Escalation to appropriate departments
        - Customer satisfaction recovery
        - Legal and compliance considerations
        - Crisis management and urgent situations
        - Relationship building and trust restoration
        
        You always prioritize customer satisfaction while ensuring company policies and legal requirements are followed.
        """
    
    def _process_request_internal(self, user_input: str, 
                                context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process escalation requests with specialized de-escalation techniques.
        
        Args:
            user_input: Customer's complaint or escalation request
            context: Additional context (previous interactions, customer history)
            
        Returns:
            Empathetic and solution-focused response
        """
        try:
            # Security: Check for urgent or crisis situations
            if self._is_urgent_situation(user_input):
                return self._handle_urgent_situation(user_input, context)
            
            # Security: Validate escalation request
            if self._is_legitimate_escalation(user_input, context):
                return self._handle_legitimate_escalation(user_input, context)
            
            # Process general escalation inquiries
            response = self._generate_escalation_response(user_input, context)
            
            # Security: Log escalation interaction
            customer_id = context.get('customer_id', 'unknown') if context else 'unknown'
            logger.info(f"Escalation inquiry processed for customer: {customer_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing escalation request: {e}")
            return "I apologize, but I encountered an issue processing your request. Please contact our escalation team directly for immediate assistance."
    
    def _is_urgent_situation(self, user_input: str) -> bool:
        """
        Check if the situation requires immediate attention.
        
        Args:
            user_input: Customer's input
            
        Returns:
            True if the situation is urgent
        """
        urgent_keywords = [
            "emergency", "urgent", "crisis", "immediate", "critical",
            "safety", "security", "legal", "police", "lawyer",
            "threat", "danger", "harm", "injury", "accident"
        ]
        
        user_input_lower = user_input.lower()
        return any(keyword in user_input_lower for keyword in urgent_keywords)
    
    def _is_legitimate_escalation(self, user_input: str, 
                                 context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate if the escalation request is legitimate.
        
        Args:
            user_input: Customer's escalation request
            context: Customer context and history
            
        Returns:
            True if the escalation is legitimate
        """
        # Check for legitimate escalation indicators
        escalation_indicators = [
            "multiple attempts", "previous contact", "unresolved",
            "policy violation", "service failure", "compensation",
            "manager", "supervisor", "higher authority"
        ]
        
        user_input_lower = user_input.lower()
        has_escalation_indicators = any(indicator in user_input_lower for indicator in escalation_indicators)
        
        # Check customer history for previous attempts
        if context and context.get("previous_attempts", 0) >= 2:
            return True
        
        return has_escalation_indicators
    
    def _handle_urgent_situation(self, user_input: str, 
                                context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle urgent situations with immediate response protocols.
        
        Args:
            user_input: Customer's urgent request
            context: Customer context
            
        Returns:
            Immediate response for urgent situations
        """
        logger.warning(f"Urgent situation detected: {user_input}")
        
        return """
        I understand this is an urgent situation that requires immediate attention.

        **Immediate Action Required:**
        - For safety or security concerns: Contact emergency services immediately
        - For legal matters: Contact our legal department directly
        - For service outages: Contact our technical emergency line

        **Emergency Contact Information:**
        - Emergency Services: 911 (if applicable)
        - Legal Department: legal@company.com
        - Technical Emergency: tech-emergency@company.com
        - Security Team: security@company.com

        **Next Steps:**
        1. I'm escalating this to our emergency response team
        2. You'll receive immediate follow-up
        3. A senior specialist will contact you within 15 minutes

        Please provide your contact information for immediate follow-up.
        """
    
    def _handle_legitimate_escalation(self, user_input: str, 
                                    context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle legitimate escalation requests with proper procedures.
        
        Args:
            user_input: Customer's escalation request
            context: Customer context and history
            
        Returns:
            Escalation response with next steps
        """
        # Create escalation case
        escalation_id = self._create_escalation_case(user_input, context)
        
        return f"""
        I understand your concern and I'm escalating this matter to ensure it receives the attention it deserves.

        **Escalation Details:**
        - Case ID: {escalation_id}
        - Escalation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        - Priority: High
        - Assigned to: Senior Specialist

        **What Happens Next:**
        1. A senior specialist will review your case within 2 hours
        2. You'll receive a detailed response within 24 hours
        3. Regular updates will be provided until resolution
        4. A follow-up call will be scheduled if needed

        **Your Rights:**
        - You have the right to speak with a supervisor
        - You can request a formal complaint investigation
        - You may be entitled to compensation if applicable
        - You can request a written response

        Please keep your case ID ({escalation_id}) for reference. You'll receive an email confirmation shortly.
        """
    
    def _create_escalation_case(self, user_input: str, 
                               context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create an escalation case with proper tracking.
        
        Args:
            user_input: Customer's escalation request
            context: Customer context
            
        Returns:
            Escalation case ID
        """
        # Generate unique case ID
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        customer_id = context.get('customer_id', 'UNKNOWN') if context else 'UNKNOWN'
        case_id = f"ESC-{customer_id}-{timestamp}"
        
        # Log escalation case creation
        logger.info(f"Escalation case created: {case_id} for customer: {customer_id}")
        
        return case_id
    
    def _generate_escalation_response(self, user_input: str, 
                                    context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate appropriate escalation response based on issue type.
        
        Args:
            user_input: Customer's complaint or escalation request
            context: Additional context
            
        Returns:
            Detailed escalation response
        """
        user_input_lower = user_input.lower()
        
        # Categorize the escalation type
        if any(word in user_input_lower for word in ["complaint", "dissatisfied", "unhappy"]):
            return self._handle_complaint(user_input, context)
        elif any(word in user_input_lower for word in ["compensation", "refund", "credit"]):
            return self._handle_compensation_request(user_input, context)
        elif any(word in user_input_lower for word in ["policy", "rule", "procedure"]):
            return self._handle_policy_dispute(user_input, context)
        elif any(word in user_input_lower for word in ["service", "quality", "failure"]):
            return self._handle_service_issue(user_input, context)
        else:
            return self._handle_general_escalation(user_input, context)
    
    def _handle_complaint(self, user_input: str, 
                         context: Optional[Dict[str, Any]] = None) -> str:
        """Handle customer complaints with empathy and resolution focus."""
        return """
        I sincerely apologize for the negative experience you've had. Your satisfaction is our top priority, and I want to make this right.

        **Understanding Your Complaint:**
        - I'm listening to understand the full situation
        - I acknowledge the impact this has had on you
        - I'm committed to finding a satisfactory resolution
        - I want to restore your trust in our service

        **Resolution Process:**
        1. I'll document your complaint thoroughly
        2. Investigate the root cause of the issue
        3. Provide a detailed response with solutions
        4. Follow up to ensure your satisfaction
        5. Implement measures to prevent future occurrences

        **What You Can Expect:**
        - A detailed response within 24 hours
        - Specific actions to address your concerns
        - Appropriate compensation if warranted
        - Follow-up to ensure resolution

        Please share the details of your experience, and I'll work to resolve this promptly.
        """
    
    def _handle_compensation_request(self, user_input: str, 
                                   context: Optional[Dict[str, Any]] = None) -> str:
        """Handle compensation and refund requests."""
        return """
        I understand you're seeking compensation for the issues you've experienced. Let me help you with this process.

        **Compensation Evaluation:**
        - Review of the specific circumstances
        - Assessment of impact and inconvenience
        - Evaluation of applicable policies
        - Determination of appropriate compensation

        **Types of Compensation Available:**
        - Service credits or account adjustments
        - Partial or full refunds
        - Extended service periods
        - Discounts on future services
        - Additional features or upgrades

        **Process:**
        1. I'll review your specific situation
        2. Evaluate against our compensation policies
        3. Propose appropriate compensation options
        4. Process approved compensation promptly
        5. Provide confirmation and follow-up

        **Documentation Required:**
        - Details of the issue experienced
        - Timeline of events
        - Any previous attempts to resolve
        - Impact on your service or experience

        Please provide specific details about your situation so I can evaluate appropriate compensation options.
        """
    
    def _handle_policy_dispute(self, user_input: str, 
                              context: Optional[Dict[str, Any]] = None) -> str:
        """Handle policy disputes and rule interpretations."""
        return """
        I understand you have concerns about our policies or procedures. Let me help clarify and address your questions.

        **Policy Review Process:**
        - Review the specific policy in question
        - Explain the reasoning behind the policy
        - Consider exceptions where appropriate
        - Provide alternative solutions if available

        **Your Rights:**
        - Right to understand our policies
        - Right to request policy exceptions
        - Right to appeal policy decisions
        - Right to speak with policy makers

        **Possible Outcomes:**
        - Policy clarification and explanation
        - Exception granted based on circumstances
        - Alternative solution provided
        - Policy review and potential modification
        - Escalation to policy decision makers

        **Documentation:**
        - I'll document your concerns
        - Review relevant policy sections
        - Provide written explanation
        - Follow up on any exceptions granted

        Please share the specific policy or procedure you have questions about, and I'll provide detailed clarification.
        """
    
    def _handle_service_issue(self, user_input: str, 
                            context: Optional[Dict[str, Any]] = None) -> str:
        """Handle service quality and failure issues."""
        return """
        I apologize for the service issues you've experienced. Quality service is our commitment, and I want to address this immediately.

        **Service Issue Resolution:**
        - Immediate investigation of the problem
        - Identification of root causes
        - Implementation of corrective actions
        - Prevention of future occurrences
        - Quality assurance review

        **Service Recovery:**
        - Immediate problem resolution
        - Service restoration or replacement
        - Quality monitoring and verification
        - Customer satisfaction follow-up
        - Process improvement implementation

        **What I Need to Help:**
        - Specific details of the service issue
        - Timeline of when the problem occurred
        - Impact on your business or use
        - Any previous attempts to resolve

        **Quality Assurance:**
        - I'll document the issue for quality review
        - Ensure proper resolution procedures
        - Implement preventive measures
        - Monitor for similar issues

        Please describe the specific service issue you've experienced, and I'll work to resolve it promptly.
        """
    
    def _handle_general_escalation(self, user_input: str, 
                                  context: Optional[Dict[str, Any]] = None) -> str:
        """Handle general escalation requests."""
        return """
        I understand you need to escalate your concern, and I'm here to help ensure it receives the proper attention.

        **Escalation Process:**
        - Thorough review of your situation
        - Assignment to appropriate specialist
        - Detailed investigation and response
        - Regular updates on progress
        - Final resolution and follow-up

        **Available Escalation Options:**
        - Senior specialist review
        - Management involvement
        - Specialized department referral
        - Formal complaint investigation
        - External mediation if appropriate

        **Your Rights During Escalation:**
        - Right to be heard and understood
        - Right to regular updates
        - Right to speak with supervisors
        - Right to formal complaint process
        - Right to appeal decisions

        **What to Expect:**
        1. Immediate acknowledgment of your escalation
        2. Assignment to appropriate specialist within 2 hours
        3. Detailed response within 24 hours
        4. Regular progress updates
        5. Final resolution and satisfaction follow-up

        Please share the details of your concern, and I'll ensure it receives the attention it deserves.
        """ 
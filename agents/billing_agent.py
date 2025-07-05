"""
Billing Agent for handling billing-related customer support inquiries.
Specializes in payment issues, invoices, refunds, and billing questions.
"""

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class BillingAgent(BaseAgent):
    """Specialized agent for handling billing and payment-related inquiries."""
    
    def __init__(self):
        """Initialize the billing agent with specialized role and goal."""
        super().__init__(
            name="Billing Specialist",
            role="Billing Support Specialist",
            goal="Resolve billing inquiries, payment issues, and invoice questions efficiently and accurately",
            verbose=True
        )
    
    def _get_backstory(self) -> str:
        """Get the billing agent's backstory and expertise."""
        return """
        You are an experienced billing specialist with 5+ years of experience in customer support.
        You have extensive knowledge of payment processing, invoicing systems, refund procedures,
        and billing policies. You are patient, detail-oriented, and always prioritize customer satisfaction
        while ensuring compliance with company policies and security protocols.
        
        Your expertise includes:
        - Payment processing and troubleshooting
        - Invoice generation and management
        - Refund and credit procedures
        - Billing dispute resolution
        - Subscription management
        - Tax and compliance issues
        
        You always verify customer identity before discussing sensitive billing information and
        follow strict security protocols to protect customer data.
        """
    
    def _process_request_internal(self, user_input: str, 
                                context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process billing-related requests with specialized knowledge.
        
        Args:
            user_input: Customer's billing inquiry
            context: Additional context (customer info, previous interactions)
            
        Returns:
            Detailed response addressing the billing inquiry
        """
        try:
            # Security: Validate context for sensitive operations
            if context and context.get("sensitive_operation"):
                return self._handle_sensitive_billing_request(user_input, context)
            
            # Process general billing inquiries
            response = self._generate_billing_response(user_input, context)
            
            # Security: Log billing interaction
            customer_id = context.get('customer_id', 'unknown') if context else 'unknown'
            logger.info(f"Billing inquiry processed for customer: {customer_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing billing request: {e}")
            return "I apologize, but I encountered an issue processing your billing inquiry. Please contact our billing department directly for immediate assistance."
    
    def _handle_sensitive_billing_request(self, user_input: str, 
                                        context: Dict[str, Any]) -> str:
        """
        Handle sensitive billing operations with enhanced security.
        
        Args:
            user_input: Customer's sensitive billing request
            context: Customer context with verification data
            
        Returns:
            Secure response for sensitive operations
        """
        # Security: Verify customer identity for sensitive operations
        if not self._verify_customer_identity(context):
            return "I'm sorry, but I need to verify your identity before I can assist with this request. Please contact our billing department directly."
        
        # Security: Check for suspicious patterns
        if self._detect_suspicious_activity(user_input):
            logger.warning(f"Suspicious billing activity detected: {user_input}")
            return "I'm sorry, but I cannot process this request. Please contact our billing department for assistance."
        
        # Process the sensitive request
        return self._generate_billing_response(user_input, context)
    
    def _verify_customer_identity(self, context: Dict[str, Any]) -> bool:
        """
        Verify customer identity for sensitive operations.
        
        Args:
            context: Customer context with verification data
            
        Returns:
            True if identity is verified, False otherwise
        """
        # Security: Basic identity verification
        required_fields = ["customer_id", "email", "phone"]
        
        for field in required_fields:
            if not context.get(field):
                logger.warning(f"Missing identity verification field: {field}")
                return False
        
        # Security: Additional verification logic can be added here
        return True
    
    def _detect_suspicious_activity(self, user_input: str) -> bool:
        """
        Detect potentially suspicious billing activity.
        
        Args:
            user_input: Customer's input
            
        Returns:
            True if suspicious activity is detected
        """
        # Security: Check for suspicious keywords
        suspicious_keywords = [
            "urgent", "emergency", "immediate", "wire transfer", "bitcoin",
            "gift card", "prepaid card", "anonymous", "secret"
        ]
        
        user_input_lower = user_input.lower()
        for keyword in suspicious_keywords:
            if keyword in user_input_lower:
                logger.warning(f"Suspicious keyword detected: {keyword}")
                return True
        
        return False
    
    def _generate_billing_response(self, user_input: str, 
                                 context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate appropriate billing response based on inquiry type.
        
        Args:
            user_input: Customer's billing inquiry
            context: Additional context
            
        Returns:
            Detailed billing response
        """
        user_input_lower = user_input.lower()
        
        # Categorize the billing inquiry
        if any(word in user_input_lower for word in ["payment", "charge", "charged"]):
            return self._handle_payment_inquiry(user_input, context)
        elif any(word in user_input_lower for word in ["invoice", "bill", "statement"]):
            return self._handle_invoice_inquiry(user_input, context)
        elif any(word in user_input_lower for word in ["refund", "return", "credit"]):
            return self._handle_refund_inquiry(user_input, context)
        elif any(word in user_input_lower for word in ["subscription", "plan", "renewal"]):
            return self._handle_subscription_inquiry(user_input, context)
        else:
            return self._handle_general_billing_inquiry(user_input, context)
    
    def _handle_payment_inquiry(self, user_input: str, 
                               context: Optional[Dict[str, Any]] = None) -> str:
        """Handle payment-related inquiries."""
        return """
        I understand you have a payment-related inquiry. Here's how I can help:

        **Payment Issues:**
        - If you're seeing an unexpected charge, I can help you understand what it's for
        - For payment method updates, you can do this securely through your account settings
        - If a payment failed, I can guide you through troubleshooting steps

        **Next Steps:**
        1. Please provide your account number or email address for verification
        2. I'll review your recent payment history
        3. I can help resolve any payment issues or questions

        For immediate assistance with urgent payment matters, please call our billing hotline.
        """
    
    def _handle_invoice_inquiry(self, user_input: str, 
                               context: Optional[Dict[str, Any]] = None) -> str:
        """Handle invoice and billing statement inquiries."""
        return """
        I can help you with your invoice and billing questions:

        **Invoice Services:**
        - View and download current and past invoices
        - Request invoice copies or adjustments
        - Understand billing line items and charges
        - Set up paperless billing

        **Common Invoice Questions:**
        - Invoice due dates and payment terms
        - Tax calculations and breakdowns
        - Service period coverage
        - Payment method information

        Please provide your account information so I can access your specific billing details.
        """
    
    def _handle_refund_inquiry(self, user_input: str, 
                              context: Optional[Dict[str, Any]] = None) -> str:
        """Handle refund and credit inquiries."""
        return """
        I can assist you with refund and credit requests:

        **Refund Process:**
        - Review your eligibility for refunds
        - Process refund requests for eligible charges
        - Provide refund status updates
        - Explain refund timelines and methods

        **Refund Eligibility:**
        - Service cancellations within grace period
        - Billing errors or duplicate charges
        - Unused service credits
        - Promotional adjustments

        Please provide details about the charge you'd like refunded, and I'll review your request.
        """
    
    def _handle_subscription_inquiry(self, user_input: str, 
                                   context: Optional[Dict[str, Any]] = None) -> str:
        """Handle subscription and plan-related inquiries."""
        return """
        I can help you with subscription and plan questions:

        **Subscription Management:**
        - Current plan details and features
        - Plan upgrades and downgrades
        - Billing cycle information
        - Auto-renewal settings

        **Plan Options:**
        - Available plans and pricing
        - Feature comparisons
        - Promotional offers
        - Cancellation policies

        Let me know what specific subscription information you need, and I'll provide the details.
        """
    
    def _handle_general_billing_inquiry(self, user_input: str, 
                                       context: Optional[Dict[str, Any]] = None) -> str:
        """Handle general billing inquiries."""
        return """
        I'm here to help with all your billing questions! Here are the main areas I can assist with:

        **Billing Services:**
        - Payment processing and troubleshooting
        - Invoice and statement questions
        - Refund and credit requests
        - Subscription and plan management
        - Billing dispute resolution

        **How to Get Started:**
        1. Please provide your account information for verification
        2. Tell me about your specific billing question or concern
        3. I'll provide detailed assistance and next steps

        For urgent billing matters, you can also call our billing department directly.
        """ 
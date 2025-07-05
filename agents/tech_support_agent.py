"""
Technical Support Agent for handling technical issues and product support.
Specializes in troubleshooting, product guidance, and technical problem resolution.
"""

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class TechSupportAgent(BaseAgent):
    """Specialized agent for handling technical support and troubleshooting."""
    
    def __init__(self):
        """Initialize the technical support agent with specialized role and goal."""
        super().__init__(
            name="Technical Support Specialist",
            role="Technical Support Specialist",
            goal="Resolve technical issues, provide product guidance, and ensure customer satisfaction through effective troubleshooting",
            verbose=True
        )
    
    def _get_backstory(self) -> str:
        """Get the technical support agent's backstory and expertise."""
        return """
        You are an experienced technical support specialist with 7+ years of experience in customer support.
        You have deep knowledge of software systems, hardware troubleshooting, network issues, and product functionality.
        You are patient, methodical, and excellent at explaining complex technical concepts in simple terms.
        
        Your expertise includes:
        - Software installation and configuration
        - Hardware troubleshooting and diagnostics
        - Network connectivity issues
        - Account access and authentication problems
        - Feature usage and product guidance
        - Performance optimization
        - Security and privacy concerns
        - Integration and API issues
        
        You follow a systematic approach to troubleshooting and always prioritize customer data security.
        """
    
    def _process_request_internal(self, user_input: str, 
                                context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process technical support requests with specialized knowledge.
        
        Args:
            user_input: Customer's technical issue or question
            context: Additional context (system info, previous attempts)
            
        Returns:
            Detailed technical support response
        """
        try:
            # Security: Validate technical request
            if self._is_security_sensitive_request(user_input):
                return self._handle_security_sensitive_request(user_input, context)
            
            # Process general technical inquiries
            response = self._generate_tech_support_response(user_input, context)
            
            # Security: Log technical support interaction
            customer_id = context.get('customer_id', 'unknown') if context else 'unknown'
            logger.info(f"Technical support inquiry processed for customer: {customer_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing technical support request: {e}")
            return "I apologize, but I encountered an issue processing your technical request. Please try again or contact our technical support team directly."
    
    def _is_security_sensitive_request(self, user_input: str) -> bool:
        """
        Check if the request involves security-sensitive operations.
        
        Args:
            user_input: Customer's technical request
            
        Returns:
            True if the request is security-sensitive
        """
        security_keywords = [
            "password", "reset", "login", "authentication", "access",
            "admin", "root", "privilege", "permission", "security",
            "encryption", "decrypt", "key", "token", "api key"
        ]
        
        user_input_lower = user_input.lower()
        return any(keyword in user_input_lower for keyword in security_keywords)
    
    def _handle_security_sensitive_request(self, user_input: str, 
                                         context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle security-sensitive technical requests with enhanced verification.
        
        Args:
            user_input: Customer's security-sensitive request
            context: Customer context with verification data
            
        Returns:
            Secure response for sensitive operations
        """
        # Security: Enhanced verification for sensitive operations
        if not self._verify_customer_for_sensitive_operations(context):
            return "I'm sorry, but I need to verify your identity before I can assist with this security-sensitive request. Please contact our security team directly."
        
        # Security: Check for suspicious patterns
        if self._detect_suspicious_technical_activity(user_input):
            logger.warning(f"Suspicious technical activity detected: {user_input}")
            return "I'm sorry, but I cannot process this request. Please contact our security team for assistance."
        
        # Process the sensitive request with appropriate guidance
        return self._generate_security_aware_response(user_input, context)
    
    def _verify_customer_for_sensitive_operations(self, context: Optional[Dict[str, Any]]) -> bool:
        """
        Verify customer identity for sensitive technical operations.
        
        Args:
            context: Customer context with verification data
            
        Returns:
            True if identity is verified for sensitive operations
        """
        if not context:
            return False
        
        # Security: Enhanced verification for sensitive operations
        required_fields = ["customer_id", "email", "phone", "account_verified"]
        
        for field in required_fields:
            if not context.get(field):
                logger.warning(f"Missing sensitive operation verification field: {field}")
                return False
        
        # Security: Check if account is verified
        if not context.get("account_verified", False):
            logger.warning("Account not verified for sensitive operations")
            return False
        
        return True
    
    def _detect_suspicious_technical_activity(self, user_input: str) -> bool:
        """
        Detect potentially suspicious technical activity.
        
        Args:
            user_input: Customer's input
            
        Returns:
            True if suspicious activity is detected
        """
        # Security: Check for suspicious technical keywords
        suspicious_keywords = [
            "hack", "exploit", "bypass", "crack", "unauthorized",
            "admin access", "root access", "privilege escalation",
            "backdoor", "malware", "virus", "trojan"
        ]
        
        user_input_lower = user_input.lower()
        for keyword in suspicious_keywords:
            if keyword in user_input_lower:
                logger.warning(f"Suspicious technical keyword detected: {keyword}")
                return True
        
        return False
    
    def _generate_tech_support_response(self, user_input: str, 
                                      context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate appropriate technical support response based on issue type.
        
        Args:
            user_input: Customer's technical issue
            context: Additional context
            
        Returns:
            Detailed technical support response
        """
        user_input_lower = user_input.lower()
        
        # Categorize the technical issue
        if any(word in user_input_lower for word in ["install", "setup", "configure"]):
            return self._handle_installation_issue(user_input, context)
        elif any(word in user_input_lower for word in ["error", "bug", "crash", "not working"]):
            return self._handle_error_issue(user_input, context)
        elif any(word in user_input_lower for word in ["slow", "performance", "lag"]):
            return self._handle_performance_issue(user_input, context)
        elif any(word in user_input_lower for word in ["network", "connection", "internet"]):
            return self._handle_network_issue(user_input, context)
        elif any(word in user_input_lower for word in ["feature", "how to", "guide"]):
            return self._handle_feature_guidance(user_input, context)
        else:
            return self._handle_general_tech_issue(user_input, context)
    
    def _generate_security_aware_response(self, user_input: str, 
                                        context: Optional[Dict[str, Any]] = None) -> str:
        """Generate security-aware response for sensitive technical requests."""
        return """
        I understand you have a security-related technical question. Here's how I can help safely:

        **Security Best Practices:**
        - Never share passwords or sensitive information in chat
        - Use secure channels for sensitive operations
        - Enable two-factor authentication when available
        - Regularly update your security settings

        **For Your Specific Request:**
        I can guide you through the proper channels and procedures to address your security concern safely.

        **Next Steps:**
        1. I'll provide general guidance on the topic
        2. Direct you to secure self-service options
        3. Escalate to our security team if needed

        Please note: For immediate security concerns, contact our security team directly.
        """
    
    def _handle_installation_issue(self, user_input: str, 
                                 context: Optional[Dict[str, Any]] = None) -> str:
        """Handle software installation and setup issues."""
        return """
        I can help you with installation and setup issues:

        **Installation Troubleshooting:**
        - System requirements verification
        - Download and installation steps
        - Common installation errors
        - Configuration after installation

        **Step-by-Step Process:**
        1. Verify your system meets minimum requirements
        2. Download from official sources only
        3. Run installation as administrator if needed
        4. Complete initial setup and configuration

        **Common Issues:**
        - Insufficient disk space
        - Missing system dependencies
        - Antivirus software conflicts
        - Permission issues

        Please provide details about your system and the specific installation issue you're experiencing.
        """
    
    def _handle_error_issue(self, user_input: str, 
                           context: Optional[Dict[str, Any]] = None) -> str:
        """Handle error messages and bug reports."""
        return """
        I can help you troubleshoot error messages and technical issues:

        **Error Resolution Process:**
        - Identify the specific error message
        - Check system logs and error codes
        - Apply targeted fixes and workarounds
        - Verify the resolution

        **Information I Need:**
        - Exact error message text
        - Steps that led to the error
        - Your system information
        - When the error started occurring

        **Common Error Types:**
        - Application crashes
        - Connection timeouts
        - Authentication failures
        - Data processing errors

        Please share the specific error message you're seeing, and I'll help you resolve it.
        """
    
    def _handle_performance_issue(self, user_input: str, 
                                context: Optional[Dict[str, Any]] = None) -> str:
        """Handle performance and speed issues."""
        return """
        I can help you optimize performance and resolve speed issues:

        **Performance Optimization:**
        - System resource monitoring
        - Cache and memory management
        - Background process optimization
        - Network speed improvements

        **Common Performance Issues:**
        - Slow application startup
        - Lag during operations
        - High CPU or memory usage
        - Network connectivity problems

        **Optimization Steps:**
        1. Check system resources (CPU, RAM, disk space)
        2. Close unnecessary background applications
        3. Clear cache and temporary files
        4. Update drivers and software
        5. Check network connection quality

        Please describe the specific performance issue you're experiencing.
        """
    
    def _handle_network_issue(self, user_input: str, 
                             context: Optional[Dict[str, Any]] = None) -> str:
        """Handle network and connectivity issues."""
        return """
        I can help you resolve network and connectivity problems:

        **Network Troubleshooting:**
        - Connection status verification
        - Router and modem diagnostics
        - DNS and IP configuration
        - Firewall and security settings

        **Common Network Issues:**
        - No internet connection
        - Slow connection speeds
        - Intermittent connectivity
        - VPN connection problems

        **Troubleshooting Steps:**
        1. Check physical connections (cables, power)
        2. Restart router and modem
        3. Test connection on other devices
        4. Check for service outages
        5. Verify network settings

        Please describe your network setup and the specific connectivity issue.
        """
    
    def _handle_feature_guidance(self, user_input: str, 
                                context: Optional[Dict[str, Any]] = None) -> str:
        """Handle feature usage and product guidance."""
        return """
        I can help you learn about product features and functionality:

        **Feature Guidance:**
        - Step-by-step tutorials
        - Feature explanations and use cases
        - Best practices and tips
        - Advanced functionality guidance

        **Available Resources:**
        - Interactive tutorials
        - Video demonstrations
        - User guides and documentation
        - Community forums and support

        **Getting Started:**
        1. Identify the specific feature you need help with
        2. I'll provide detailed guidance
        3. Walk through practical examples
        4. Answer any follow-up questions

        Please let me know which feature or functionality you'd like to learn about.
        """
    
    def _handle_general_tech_issue(self, user_input: str, 
                                  context: Optional[Dict[str, Any]] = None) -> str:
        """Handle general technical support inquiries."""
        return """
        I'm here to help with all your technical questions and issues! Here are the main areas I can assist with:

        **Technical Support Services:**
        - Software installation and configuration
        - Error troubleshooting and bug resolution
        - Performance optimization
        - Network and connectivity issues
        - Feature usage and product guidance
        - Account access and authentication
        - Security and privacy concerns

        **How to Get Started:**
        1. Describe your technical issue or question
        2. Provide relevant system information
        3. I'll provide targeted assistance and solutions
        4. Follow up with additional questions as needed

        For urgent technical issues, you can also contact our technical support team directly.
        """ 
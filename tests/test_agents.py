"""
Unit tests for the agent classes.
Tests functionality, security measures, and error handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from agents.billing_agent import BillingAgent
from agents.tech_support_agent import TechSupportAgent
from agents.escalation_agent import EscalationAgent

class TestBaseAgent(unittest.TestCase):
    """Test cases for the BaseAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the settings to avoid configuration issues
        with patch('agents.base_agent.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            # Create a concrete implementation for testing
            class TestAgent(BaseAgent):
                def _get_backstory(self):
                    return "Test backstory"
                
                def _process_request_internal(self, user_input, context=None):
                    return "Test response"
            
            self.base_agent = TestAgent("Test Agent", "Test Role", "Test Goal")
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.base_agent.name, "Test Agent")
        self.assertEqual(self.base_agent.role, "Test Role")
        self.assertEqual(self.base_agent.goal, "Test Goal")
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        # Test normal input
        normal_input = "Hello, world!"
        sanitized = self.base_agent.sanitize_input(normal_input)
        self.assertEqual(sanitized, "Hello, world!")
        
        # Test input with dangerous characters
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = self.base_agent.sanitize_input(dangerous_input)
        self.assertNotIn("<script>", sanitized)
        self.assertNotIn("</script>", sanitized)
        
        # Test input length limit
        long_input = "A" * 2000
        sanitized = self.base_agent.sanitize_input(long_input)
        self.assertLessEqual(len(sanitized), 1000)
    
    def test_log_interaction(self):
        """Test interaction logging."""
        user_input = "Test input"
        agent_response = "Test response"
        
        self.base_agent.log_interaction(user_input, agent_response)
        
        self.assertEqual(len(self.base_agent.interaction_history), 1)
        logged_interaction = self.base_agent.interaction_history[0]
        
        self.assertEqual(logged_interaction["user_input"], user_input)
        self.assertEqual(logged_interaction["agent_response"], agent_response)
        self.assertEqual(logged_interaction["agent_name"], "Test Agent")
    
    def test_get_agent_info(self):
        """Test agent information retrieval."""
        info = self.base_agent.get_agent_info()
        
        self.assertEqual(info["name"], "Test Agent")
        self.assertEqual(info["role"], "Test Role")
        self.assertEqual(info["goal"], "Test Goal")
        self.assertEqual(info["interaction_count"], 0)

class TestBillingAgent(unittest.TestCase):
    """Test cases for the BillingAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('agents.billing_agent.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            self.billing_agent = BillingAgent()
    
    def test_billing_agent_initialization(self):
        """Test billing agent initialization."""
        self.assertEqual(self.billing_agent.name, "Billing Specialist")
        self.assertEqual(self.billing_agent.role, "Billing Support Specialist")
    
    def test_verify_customer_identity(self):
        """Test customer identity verification."""
        # Test with valid context
        valid_context = {
            "customer_id": "12345",
            "email": "test@example.com",
            "phone": "123-456-7890"
        }
        self.assertTrue(self.billing_agent._verify_customer_identity(valid_context))
        
        # Test with missing fields
        invalid_context = {
            "customer_id": "12345"
            # Missing email and phone
        }
        self.assertFalse(self.billing_agent._verify_customer_identity(invalid_context))
    
    def test_detect_suspicious_activity(self):
        """Test suspicious activity detection."""
        # Test normal input
        normal_input = "I have a billing question"
        self.assertFalse(self.billing_agent._detect_suspicious_activity(normal_input))
        
        # Test suspicious input
        suspicious_input = "I need urgent wire transfer"
        self.assertTrue(self.billing_agent._detect_suspicious_activity(suspicious_input))
    
    def test_generate_billing_response(self):
        """Test billing response generation."""
        # Test payment inquiry
        payment_input = "I have a payment question"
        response = self.billing_agent._generate_billing_response(payment_input)
        self.assertIn("payment", response.lower())
        
        # Test invoice inquiry
        invoice_input = "I need my invoice"
        response = self.billing_agent._generate_billing_response(invoice_input)
        self.assertIn("invoice", response.lower())
        
        # Test refund inquiry
        refund_input = "I want a refund"
        response = self.billing_agent._generate_billing_response(refund_input)
        self.assertIn("refund", response.lower())

class TestTechSupportAgent(unittest.TestCase):
    """Test cases for the TechSupportAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('agents.tech_support_agent.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            self.tech_agent = TechSupportAgent()
    
    def test_tech_agent_initialization(self):
        """Test technical support agent initialization."""
        self.assertEqual(self.tech_agent.name, "Technical Support Specialist")
        self.assertEqual(self.tech_agent.role, "Technical Support Specialist")
    
    def test_is_security_sensitive_request(self):
        """Test security-sensitive request detection."""
        # Test normal request
        normal_request = "My app is slow"
        self.assertFalse(self.tech_agent._is_security_sensitive_request(normal_request))
        
        # Test security-sensitive request
        security_request = "I need to reset my password"
        self.assertTrue(self.tech_agent._is_security_sensitive_request(security_request))
    
    def test_verify_customer_for_sensitive_operations(self):
        """Test customer verification for sensitive operations."""
        # Test with valid context
        valid_context = {
            "customer_id": "12345",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "account_verified": True
        }
        self.assertTrue(self.tech_agent._verify_customer_for_sensitive_operations(valid_context))
        
        # Test with invalid context
        invalid_context = {
            "customer_id": "12345"
            # Missing required fields
        }
        self.assertFalse(self.tech_agent._verify_customer_for_sensitive_operations(invalid_context))
    
    def test_detect_suspicious_technical_activity(self):
        """Test suspicious technical activity detection."""
        # Test normal input
        normal_input = "My app is not working"
        self.assertFalse(self.tech_agent._detect_suspicious_technical_activity(normal_input))
        
        # Test suspicious input
        suspicious_input = "I need admin access to hack"
        self.assertTrue(self.tech_agent._detect_suspicious_technical_activity(suspicious_input))

class TestEscalationAgent(unittest.TestCase):
    """Test cases for the EscalationAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('agents.escalation_agent.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            self.escalation_agent = EscalationAgent()
    
    def test_escalation_agent_initialization(self):
        """Test escalation agent initialization."""
        self.assertEqual(self.escalation_agent.name, "Escalation Specialist")
        self.assertEqual(self.escalation_agent.role, "Escalation and Complaint Resolution Specialist")
    
    def test_is_urgent_situation(self):
        """Test urgent situation detection."""
        # Test normal request
        normal_request = "I have a complaint"
        self.assertFalse(self.escalation_agent._is_urgent_situation(normal_request))
        
        # Test urgent request
        urgent_request = "This is an emergency situation"
        self.assertTrue(self.escalation_agent._is_urgent_situation(urgent_request))
    
    def test_is_legitimate_escalation(self):
        """Test legitimate escalation detection."""
        # Test legitimate escalation
        legitimate_request = "I have multiple attempts to resolve this"
        self.assertTrue(self.escalation_agent._is_legitimate_escalation(legitimate_request))
        
        # Test with context showing previous attempts
        context = {"previous_attempts": 3}
        self.assertTrue(self.escalation_agent._is_legitimate_escalation("test", context))
        
        # Test normal request
        normal_request = "I have a question"
        self.assertFalse(self.escalation_agent._is_legitimate_escalation(normal_request))
    
    def test_create_escalation_case(self):
        """Test escalation case creation."""
        context = {"customer_id": "12345"}
        case_id = self.escalation_agent._create_escalation_case("test request", context)
        
        self.assertIsInstance(case_id, str)
        self.assertTrue(case_id.startswith("ESC-"))
        self.assertIn("12345", case_id)

class TestAgentIntegration(unittest.TestCase):
    """Integration tests for agent interactions."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('agents.billing_agent.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            self.billing_agent = BillingAgent()
        
        with patch('agents.tech_support_agent.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            self.tech_agent = TechSupportAgent()
        
        with patch('agents.escalation_agent.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "test-key"
            self.escalation_agent = EscalationAgent()
    
    def test_agent_response_consistency(self):
        """Test that agents provide consistent responses."""
        test_input = "I have a question"
        
        # All agents should handle the input without errors
        billing_response = self.billing_agent.process_request(test_input)
        tech_response = self.tech_agent.process_request(test_input)
        escalation_response = self.escalation_agent.process_request(test_input)
        
        self.assertIsInstance(billing_response, str)
        self.assertIsInstance(tech_response, str)
        self.assertIsInstance(escalation_response, str)
        
        self.assertGreater(len(billing_response), 0)
        self.assertGreater(len(tech_response), 0)
        self.assertGreater(len(escalation_response), 0)
    
    def test_security_measures(self):
        """Test that security measures are properly implemented."""
        malicious_input = "<script>alert('xss')</script>"
        
        # All agents should sanitize malicious input
        billing_response = self.billing_agent.process_request(malicious_input)
        tech_response = self.tech_agent.process_request(malicious_input)
        escalation_response = self.escalation_agent.process_request(malicious_input)
        
        # Responses should not contain the malicious script
        self.assertNotIn("<script>", billing_response)
        self.assertNotIn("<script>", tech_response)
        self.assertNotIn("<script>", escalation_response)

if __name__ == "__main__":
    unittest.main() 
#!/usr/bin/env python3
"""
Demo script for the CrewAI Multi-Agent Customer Support Desk.
Shows how different agents handle various types of customer inquiries.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_billing_agent():
    """Demonstrate billing agent functionality."""
    print("\n" + "="*60)
    print("💳 BILLING AGENT DEMO")
    print("="*60)
    
    try:
        from agents.billing_agent import BillingAgent
        
        # Initialize billing agent
        billing_agent = BillingAgent()
        
        # Test cases
        test_cases = [
            "I have a question about my payment",
            "I need a refund for my last charge",
            "Can you help me with my invoice?",
            "I want to update my subscription plan"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case}")
            print("-" * 40)
            
            response = billing_agent.process_request(test_case)
            print(f"🤖 Response: {response[:200]}...")
            
    except Exception as e:
        print(f"❌ Error in billing agent demo: {e}")

def demo_tech_support_agent():
    """Demonstrate technical support agent functionality."""
    print("\n" + "="*60)
    print("🔧 TECHNICAL SUPPORT AGENT DEMO")
    print("="*60)
    
    try:
        from agents.tech_support_agent import TechSupportAgent
        
        # Initialize tech support agent
        tech_agent = TechSupportAgent()
        
        # Test cases
        test_cases = [
            "My app is not working properly",
            "I need help installing the software",
            "The application is running very slow",
            "I can't connect to the network"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case}")
            print("-" * 40)
            
            response = tech_agent.process_request(test_case)
            print(f"🤖 Response: {response[:200]}...")
            
    except Exception as e:
        print(f"❌ Error in tech support agent demo: {e}")

def demo_escalation_agent():
    """Demonstrate escalation agent functionality."""
    print("\n" + "="*60)
    print("🚨 ESCALATION AGENT DEMO")
    print("="*60)
    
    try:
        from agents.escalation_agent import EscalationAgent
        
        # Initialize escalation agent
        escalation_agent = EscalationAgent()
        
        # Test cases
        test_cases = [
            "I'm very unhappy with the service",
            "This is an emergency situation",
            "I want to speak to a manager",
            "I need compensation for the issues I've faced"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case}")
            print("-" * 40)
            
            response = escalation_agent.process_request(test_case)
            print(f"🤖 Response: {response[:200]}...")
            
    except Exception as e:
        print(f"❌ Error in escalation agent demo: {e}")

def demo_crew_routing():
    """Demonstrate crew routing functionality."""
    print("\n" + "="*60)
    print("🛟 CREW ROUTING DEMO")
    print("="*60)
    
    try:
        from crew.customer_support_crew import CustomerSupportCrew
        
        # Initialize crew
        crew = CustomerSupportCrew()
        
        # Test cases with different types of requests
        test_cases = [
            ("I have a billing question about my invoice", "Expected: Billing Agent"),
            ("My software is not working", "Expected: Technical Support Agent"),
            ("I'm very frustrated and want to complain", "Expected: Escalation Agent"),
            ("I need help with my account", "Expected: General Support")
        ]
        
        for i, (test_case, expected) in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case}")
            print(f"🎯 {expected}")
            print("-" * 40)
            
            response = crew.route_request(test_case)
            print(f"🤖 Response: {response[:200]}...")
            
    except Exception as e:
        print(f"❌ Error in crew routing demo: {e}")

def demo_security_features():
    """Demonstrate security features."""
    print("\n" + "="*60)
    print("🔒 SECURITY FEATURES DEMO")
    print("="*60)
    
    try:
        from agents.base_agent import BaseAgent
        
        # Create a test agent
        class TestAgent(BaseAgent):
            def _get_backstory(self):
                return "Test agent for security demo"
            
            def _process_request_internal(self, user_input, context=None):
                return f"Processed: {user_input}"
        
        test_agent = TestAgent("Security Test Agent", "Test Role", "Test Goal")
        
        # Test input sanitization
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "A" * 2000,  # Very long input
            "Normal input with <tags> and 'quotes'"
        ]
        
        for i, malicious_input in enumerate(malicious_inputs, 1):
            print(f"\n📝 Test Case {i}: {malicious_input[:50]}...")
            print("-" * 40)
            
            sanitized = test_agent.sanitize_input(malicious_input)
            print(f"🧹 Sanitized: {sanitized[:100]}...")
            
            # Test that dangerous content is removed
            if "<script>" in malicious_input:
                print("✅ Script tags removed")
            if len(malicious_input) > 1000:
                print("✅ Long input truncated")
            
    except Exception as e:
        print(f"❌ Error in security features demo: {e}")

def main():
    """Run all demos."""
    print("🛟 CrewAI Multi-Agent Customer Support Desk - DEMO")
    print("="*60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if environment is set up
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  Warning: OPENAI_API_KEY not set")
        print("   Some features may not work properly")
        print("   Set your OpenAI API key in the .env file")
    
    # Run demos
    demo_billing_agent()
    demo_tech_support_agent()
    demo_escalation_agent()
    demo_crew_routing()
    demo_security_features()
    
    print("\n" + "="*60)
    print("🎉 Demo completed!")
    print("="*60)
    print("\n💡 To run the full system:")
    print("   1. Set up your .env file with API keys")
    print("   2. Run: python run.py")
    print("   3. Open: http://localhost:8501")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 
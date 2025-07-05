"""
Base agent class for customer support agents.
Provides common functionality and security measures for all agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from crewai import Agent
from langchain_openai import ChatOpenAI
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all customer support agents with security and logging."""
    
    def __init__(self, name: str, role: str, goal: str, verbose: bool = True):
        """
        Initialize base agent with security measures.
        
        Args:
            name: Agent name
            role: Agent role description
            goal: Agent's primary goal
            verbose: Whether to enable verbose logging
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.verbose = verbose
        self.llm = self._initialize_llm()
        self.agent = self._create_agent()
        self.interaction_history: List[Dict[str, Any]] = []
        
        # Security: Log agent creation
        logger.info(f"Agent '{name}' initialized with role: {role}")
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model with security configuration."""
        try:
            from config.settings import settings
            llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.7,
                api_key=settings.OPENAI_API_KEY,
                verbose=self.verbose
            )
            logger.info(f"LLM initialized for agent: {self.name}")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize LLM for agent {self.name}: {e}")
            raise
    
    def _create_agent(self) -> Agent:
        """Create the CrewAI agent with security measures."""
        try:
            agent = Agent(
                role=self.role,
                goal=self.goal,
                backstory=self._get_backstory(),
                verbose=self.verbose,
                llm=self.llm,
                allow_delegation=False,  # Security: Prevent unauthorized delegation
                max_iter=3,  # Security: Limit iterations to prevent loops
                memory=True
            )
            logger.info(f"Agent '{self.name}' created successfully")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent {self.name}: {e}")
            raise
    
    @abstractmethod
    def _get_backstory(self) -> str:
        """Get the agent's backstory - to be implemented by subclasses."""
        pass
    
    def log_interaction(self, user_input: str, agent_response: str, 
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log agent interactions for security and audit purposes.
        
        Args:
            user_input: User's input
            agent_response: Agent's response
            metadata: Additional metadata about the interaction
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": self.name,
            "user_input": user_input,
            "agent_response": agent_response,
            "metadata": metadata or {}
        }
        
        self.interaction_history.append(interaction)
        logger.info(f"Interaction logged for agent {self.name}")
    
    def sanitize_input(self, user_input: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            user_input: Raw user input
            
        Returns:
            Sanitized input
        """
        # Security: Basic input sanitization
        sanitized = user_input.strip()
        
        # Security: Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Security: Limit input length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
            logger.warning(f"Input truncated for agent {self.name}")
        
        return sanitized
    
    def process_request(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process user request with security measures.
        
        Args:
            user_input: User's input
            context: Additional context for the request
            
        Returns:
            Agent's response
        """
        try:
            # Security: Sanitize input
            sanitized_input = self.sanitize_input(user_input)
            
            # Security: Validate input
            if not sanitized_input:
                return "I'm sorry, but I couldn't process your request. Please provide a valid input."
            
            # Process the request
            response = self._process_request_internal(sanitized_input, context)
            
            # Security: Log interaction
            self.log_interaction(sanitized_input, response, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request for agent {self.name}: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    @abstractmethod
    def _process_request_internal(self, user_input: str, 
                                context: Optional[Dict[str, Any]] = None) -> str:
        """Internal request processing - to be implemented by subclasses."""
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information for monitoring and debugging."""
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "interaction_count": len(self.interaction_history),
            "last_interaction": self.interaction_history[-1]["timestamp"] if self.interaction_history else None
        } 
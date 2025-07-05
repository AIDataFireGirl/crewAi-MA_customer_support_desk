"""
FastAPI application for the Customer Support Desk.
Provides REST API endpoints with security measures and rate limiting.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import time
from crew.customer_support_crew import CustomerSupportCrew
from config.settings import settings
import jwt
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Customer Support Desk API",
    description="Multi-Agent Customer Support System using CrewAI",
    version="1.0.0"
)

# Security configuration
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate limiting
rate_limit_store: Dict[str, float] = {}

# Initialize customer support crew
customer_support_crew = CustomerSupportCrew()

# CORS middleware for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class CustomerRequest(BaseModel):
    """Model for customer support requests."""
    message: str = Field(..., min_length=1, max_length=1000, description="Customer's message")
    customer_id: Optional[str] = Field(None, description="Customer ID for tracking")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    emergency: bool = Field(False, description="Whether this is an emergency request")

class CustomerResponse(BaseModel):
    """Model for customer support responses."""
    response: str = Field(..., description="Agent's response")
    agent_type: str = Field(..., description="Type of agent that handled the request")
    timestamp: str = Field(..., description="Response timestamp")
    case_id: Optional[str] = Field(None, description="Case ID if escalation is involved")

class CrewStatus(BaseModel):
    """Model for crew status information."""
    crew_status: str = Field(..., description="Current crew status")
    agents: Dict[str, Any] = Field(..., description="Agent information")
    total_interactions: int = Field(..., description="Total interactions across all agents")
    last_updated: str = Field(..., description="Last update timestamp")

# Security functions
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify JWT token for API access.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def check_rate_limit(customer_id: str) -> bool:
    """
    Check rate limiting for customer requests.
    
    Args:
        customer_id: Customer identifier
        
    Returns:
        True if request is allowed, False if rate limited
    """
    current_time = time.time()
    window_start = current_time - 60  # 1 minute window
    
    # Clean old entries
    rate_limit_store = {k: v for k, v in rate_limit_store.items() if v > window_start}
    
    # Check rate limit
    customer_requests = [t for t in rate_limit_store.values() if t > window_start]
    
    if len(customer_requests) >= settings.RATE_LIMIT_PER_MINUTE:
        return False
    
    # Add current request
    rate_limit_store[customer_id] = current_time
    return True

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: Raw input text
        
    Returns:
        Sanitized text
    """
    # Security: Basic input sanitization
    sanitized = text.strip()
    
    # Security: Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', 'script', 'javascript']
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Security: Limit input length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
        logger.warning("Input truncated due to length limit")
    
    return sanitized

# API endpoints
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "message": "Customer Support Desk API is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/support/request", response_model=CustomerResponse, tags=["Support"])
async def handle_support_request(
    request: CustomerRequest,
    token: Dict[str, Any] = Depends(verify_token)
):
    """
    Handle customer support requests with automatic routing to appropriate agents.
    
    Args:
        request: Customer support request
        token: Verified JWT token
        
    Returns:
        Response from appropriate agent
    """
    try:
        # Security: Rate limiting
        customer_id = request.customer_id or "anonymous"
        if not check_rate_limit(customer_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Security: Input sanitization
        sanitized_message = sanitize_input(request.message)
        
        # Security: Validate input
        if not sanitized_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid message content"
            )
        
        # Handle emergency requests
        if request.emergency:
            response = customer_support_crew.handle_emergency(sanitized_message, request.context)
            agent_type = "escalation"
        else:
            # Route to appropriate agent
            response = customer_support_crew.route_request(sanitized_message, request.context)
            agent_type = "auto_routed"
        
        # Log successful request
        logger.info(f"Support request processed for customer: {customer_id}")
        
        return CustomerResponse(
            response=response,
            agent_type=agent_type,
            timestamp=datetime.now().isoformat(),
            case_id=None  # Will be populated for escalations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing support request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/support/complex", response_model=CustomerResponse, tags=["Support"])
async def handle_complex_request(
    request: CustomerRequest,
    token: Dict[str, Any] = Depends(verify_token)
):
    """
    Handle complex requests that require multiple agents.
    
    Args:
        request: Complex customer support request
        token: Verified JWT token
        
    Returns:
        Comprehensive response from multiple agents
    """
    try:
        # Security: Rate limiting
        customer_id = request.customer_id or "anonymous"
        if not check_rate_limit(customer_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Security: Input sanitization
        sanitized_message = sanitize_input(request.message)
        
        # Process complex request with multiple agents
        result = customer_support_crew.process_complex_request(sanitized_message, request.context)
        
        # Log successful complex request
        logger.info(f"Complex request processed for customer: {customer_id}")
        
        return CustomerResponse(
            response=result.get("response", "No response available"),
            agent_type="multi_agent",
            timestamp=datetime.now().isoformat(),
            case_id=None
        )
        
    except Exception as e:
        logger.error(f"Error processing complex request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/support/status", response_model=CrewStatus, tags=["Monitoring"])
async def get_crew_status(token: Dict[str, Any] = Depends(verify_token)):
    """
    Get the current status of all agents in the crew.
    
    Args:
        token: Verified JWT token
        
    Returns:
        Current crew status and agent information
    """
    try:
        status_info = customer_support_crew.get_crew_status()
        
        return CrewStatus(
            crew_status=status_info["crew_status"],
            agents=status_info["agents"],
            total_interactions=status_info["total_interactions"],
            last_updated=status_info["last_updated"]
        )
        
    except Exception as e:
        logger.error(f"Error getting crew status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/support/billing", response_model=CustomerResponse, tags=["Specialized"])
async def handle_billing_request(
    request: CustomerRequest,
    token: Dict[str, Any] = Depends(verify_token)
):
    """
    Handle billing-specific requests directly.
    
    Args:
        request: Billing-related request
        token: Verified JWT token
        
    Returns:
        Response from billing agent
    """
    try:
        # Security: Rate limiting
        customer_id = request.customer_id or "anonymous"
        if not check_rate_limit(customer_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Security: Input sanitization
        sanitized_message = sanitize_input(request.message)
        
        # Route directly to billing agent
        response = customer_support_crew.billing_agent.process_request(sanitized_message, request.context)
        
        logger.info(f"Billing request processed for customer: {customer_id}")
        
        return CustomerResponse(
            response=response,
            agent_type="billing",
            timestamp=datetime.now().isoformat(),
            case_id=None
        )
        
    except Exception as e:
        logger.error(f"Error processing billing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/support/technical", response_model=CustomerResponse, tags=["Specialized"])
async def handle_technical_request(
    request: CustomerRequest,
    token: Dict[str, Any] = Depends(verify_token)
):
    """
    Handle technical support requests directly.
    
    Args:
        request: Technical support request
        token: Verified JWT token
        
    Returns:
        Response from technical support agent
    """
    try:
        # Security: Rate limiting
        customer_id = request.customer_id or "anonymous"
        if not check_rate_limit(customer_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Security: Input sanitization
        sanitized_message = sanitize_input(request.message)
        
        # Route directly to technical support agent
        response = customer_support_crew.tech_support_agent.process_request(sanitized_message, request.context)
        
        logger.info(f"Technical request processed for customer: {customer_id}")
        
        return CustomerResponse(
            response=response,
            agent_type="technical",
            timestamp=datetime.now().isoformat(),
            case_id=None
        )
        
    except Exception as e:
        logger.error(f"Error processing technical request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/support/escalation", response_model=CustomerResponse, tags=["Specialized"])
async def handle_escalation_request(
    request: CustomerRequest,
    token: Dict[str, Any] = Depends(verify_token)
):
    """
    Handle escalation requests directly.
    
    Args:
        request: Escalation request
        token: Verified JWT token
        
    Returns:
        Response from escalation agent
    """
    try:
        # Security: Rate limiting
        customer_id = request.customer_id or "anonymous"
        if not check_rate_limit(customer_id):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Security: Input sanitization
        sanitized_message = sanitize_input(request.message)
        
        # Route directly to escalation agent
        response = customer_support_crew.escalation_agent.process_request(sanitized_message, request.context)
        
        logger.info(f"Escalation request processed for customer: {customer_id}")
        
        return CustomerResponse(
            response=response,
            agent_type="escalation",
            timestamp=datetime.now().isoformat(),
            case_id=None
        )
        
    except Exception as e:
        logger.error(f"Error processing escalation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper logging."""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with proper logging."""
    logger.error(f"General Exception: {str(exc)}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
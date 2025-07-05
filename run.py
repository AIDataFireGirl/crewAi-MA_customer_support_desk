#!/usr/bin/env python3
"""
Main run script for the CrewAI Multi-Agent Customer Support Desk.
Provides easy startup for both API server and web interface.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'crewai', 'fastapi', 'streamlit', 'openai', 'langchain'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def check_environment():
    """Check if environment variables are properly configured."""
    required_env_vars = ['OPENAI_API_KEY', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        return False
    
    print("✅ Environment variables are configured")
    return True

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = ['logs', 'data']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created/verified")

def start_api_server():
    """Start the FastAPI server."""
    print("🚀 Starting API server...")
    
    try:
        # Start the API server
        api_process = subprocess.Popen([
            sys.executable, 'api/main.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        if api_process.poll() is None:
            print("✅ API server started successfully")
            return api_process
        else:
            stdout, stderr = api_process.communicate()
            print(f"❌ Failed to start API server: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def start_web_interface():
    """Start the Streamlit web interface."""
    print("🌐 Starting web interface...")
    
    try:
        # Start the Streamlit app
        web_process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'web_interface/app.py',
            '--server.port', '8501',
            '--server.address', 'localhost'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for the interface to start
        time.sleep(5)
        
        if web_process.poll() is None:
            print("✅ Web interface started successfully")
            return web_process
        else:
            stdout, stderr = web_process.communicate()
            print(f"❌ Failed to start web interface: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        return None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\n🛑 Shutting down services...")
    sys.exit(0)

def main():
    """Main function to start the customer support desk."""
    print("=" * 60)
    print("🛟 CrewAI Multi-Agent Customer Support Desk")
    print("=" * 60)
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Pre-flight checks
    print("\n🔍 Running pre-flight checks...")
    
    if not check_dependencies():
        sys.exit(1)
    
    if not check_environment():
        print("\n💡 To set up environment variables:")
        print("1. Copy env_example.txt to .env")
        print("2. Add your OpenAI API key")
        print("3. Set a secure secret key")
        sys.exit(1)
    
    create_directories()
    
    print("\n🎯 Starting services...")
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Failed to start API server. Exiting.")
        sys.exit(1)
    
    # Start web interface
    web_process = start_web_interface()
    if not web_process:
        print("❌ Failed to start web interface. Stopping API server.")
        api_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Customer Support Desk is now running!")
    print("=" * 60)
    print("📱 Web Interface: http://localhost:8501")
    print("🔌 API Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n💡 Press Ctrl+C to stop all services")
    print("=" * 60)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
                
            if web_process.poll() is not None:
                print("❌ Web interface stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal...")
    
    finally:
        # Cleanup
        print("🧹 Cleaning up processes...")
        
        if api_process and api_process.poll() is None:
            api_process.terminate()
            api_process.wait()
            print("✅ API server stopped")
        
        if web_process and web_process.poll() is None:
            web_process.terminate()
            web_process.wait()
            print("✅ Web interface stopped")
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 
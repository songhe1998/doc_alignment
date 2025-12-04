"""
Helper module for OpenAI client initialization with proper connection handling
"""

import openai
import httpx
import socket

def create_openai_client(api_key: str) -> openai.OpenAI:
    """
    Create an OpenAI client with proper httpx configuration to avoid connection issues.
    
    This fixes the "Can't assign requested address" error on macOS by:
    1. Using custom connection limits
    2. Setting proper timeouts
    3. Configuring socket options
    
    Args:
        api_key: OpenAI API key
        
    Returns:
        Configured OpenAI client
    """
    # Create httpx client with custom configuration
    # Note: Removed local_address binding to avoid "Can't assign requested address" error
    # when multiple network interfaces/VPNs are present
    http_client = httpx.Client(
        limits=httpx.Limits(
            max_connections=5,
            max_keepalive_connections=2,
            keepalive_expiry=30.0
        ),
        timeout=httpx.Timeout(
            connect=10.0,
            read=60.0,
            write=10.0,
            pool=10.0
        ),
        follow_redirects=True,
        transport=httpx.HTTPTransport(
            retries=2
        )
    )
    
    # Create OpenAI client with custom http_client
    client = openai.OpenAI(
        api_key=api_key,
        http_client=http_client,
        max_retries=2
    )
    
    return client


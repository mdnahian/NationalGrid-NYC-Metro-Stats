#!/usr/bin/env python3
"""
Simple Flask app to serve National Grid NYC Metro usage data.
"""

import os
import asyncio
from flask import Flask, jsonify
import sys

# Import from internal folder
from internal.nationalgridmetro import NationalGridMetroClient

app = Flask(__name__)

async def get_usage_data():
    """Get usage data using the National Grid client."""
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    
    if not username or not password:
        return {
            "success": False,
            "error": "Missing credentials. Please set USERNAME and PASSWORD environment variables."
        }
    
    client = NationalGridMetroClient()
    
    try:
        # Step 1: Check for existing valid tokens
        cached_result = client.load_tokens()
        if cached_result:
            # If we don't have customer URN, we need to get it
            if not client.customer_urn:
                customer_result = await client.get_customer_data()
                if not customer_result["success"]:
                    # If customer data fails, maybe token is invalid, try fresh login
                    cached_result = None
        
        # Step 2: If no valid cache, do fresh login
        if not cached_result:
            login_result = await client.login_and_get_tokens(username, password)
            if not login_result["success"]:
                return login_result
            
            # Get customer data after fresh login
            customer_result = await client.get_customer_data()
            if not customer_result["success"]:
                return customer_result
        
        # Step 3: Get usage and cost data
        usage_result = await client.get_usage_and_cost_data()
        return usage_result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

@app.route('/usage', methods=['GET'])
def get_usage():
    """API endpoint to get National Grid usage data."""
    try:
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(get_usage_data())
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "National Grid NYC Metro Usage API"
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information."""
    return jsonify({
        "service": "National Grid NYC Metro Usage API",
        "endpoints": {
            "/": "This information page",
            "/health": "Health check",
            "/usage": "Get usage and cost data"
        },
        "environment_variables_required": [
            "USERNAME",
            "PASSWORD"
        ]
    })

if __name__ == '__main__':
    # Check if required environment variables are set
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    
    if not username or not password:
        print("Error: Missing required environment variables:")
        print("  USERNAME")
        print("  PASSWORD")
        print("\nExample usage:")
        print("  export USERNAME='your_username'")
        print("  export PASSWORD='your_password'")
        print("  python app/app.py")
        sys.exit(1)
    
    app.run(host='0.0.0.0', port=50583, debug=True) 
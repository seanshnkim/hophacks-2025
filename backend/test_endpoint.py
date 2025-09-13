#!/usr/bin/env python3
"""
Simple test script to hit the /learn endpoint and save the playground as an .ipynb file
"""

import requests
import json
from datetime import datetime

def main():
    # API endpoint
    url = "http://localhost:8000/learn"
    
    # Request payload
    payload = {
        "topic": "python variables",
        "user_preferences": "I am a beginner"
    }
    
    print(f"Testing endpoint with topic: '{payload['topic']}'")
    print(f"User preferences: '{payload['user_preferences']}'")
    print(f"URL: {url}")
    print("-" * 50)
    
    try:
        # Make the request
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Request successful!")
            print(f"Topic: {data['topic']}")
            print(f"Learning module length: {len(data['learning_module'])} characters")
            print(f"Playground cells: {len(data['playground'].get('cells', []))}")
            
            # Save playground as .ipynb file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"playground_{timestamp}.ipynb"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data['playground'], f, indent=2, ensure_ascii=False)
            
            print(f"💾 Playground saved as: {output_file}")
            print("🎉 Test completed successfully!")
            
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
        print("   Start the server with: python run.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()

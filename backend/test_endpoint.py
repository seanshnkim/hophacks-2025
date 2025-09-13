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
        "topic": "linear functions",
        "user_preferences": "I want to see visual examples"
    }
    
    print(f"Testing endpoint with topic: '{payload['topic']}'")
    print(f"User preferences: '{payload['user_preferences']}'")
    print(f"URL: {url}")
    print("-" * 50)
    
    try:
        # Make the request
        response = requests.post(url, json=payload, timeout=300)
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ Request successful!")
            print(f"Main topic: {data['main_topic']}")
            print(f"Components: {data['components']}")
            print(f"Number of learning blocks: {len(data['learning_blocks'])}")
            print(f"Playground cells: {len(data['playground'].get('cells', []))}")
            
            # Display learning blocks
            print("\n📚 Learning Blocks:")
            for block in data['learning_blocks']:
                print(f"  Block {block['id']}: {block['topic']}")
                print(f"    Content: {len(block['text_content'])} characters")
                if block['visualization_path']:
                    print(f"    🎥 Visualization: {block['visualization_path']}")
                else:
                    print(f"    ℹ️  No visualization")
            
            # Test visualization endpoint if we have a visualization
            for block in data['learning_blocks']:
                if block['visualization_path']:
                    viz_url = f"http://localhost:8000/visualization/{block['visualization_path']}"
                    print(f"\n🎥 Testing visualization endpoint: {viz_url}")
                    
                    viz_response = requests.get(viz_url)
                    if viz_response.status_code == 200:
                        print(f"✅ Visualization endpoint working! ({len(viz_response.content)} bytes)")
                    else:
                        print(f"❌ Visualization endpoint failed: {viz_response.status_code}")
                    break
            
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

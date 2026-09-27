import requests
import json
import time

def debug_ollama():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2:0.5b",
        "prompt": "Hello",
        "stream": False
    }
    
    print("--- DEBUGGING OLLAMA CONNECTION ---")
    try:
        print(f"Requesting model: {payload['model']}...")
        response = requests.post(url, json=payload, timeout=30)
        print(f"HTTP Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: Server responded correctly.")
            print("Response Body:", response.text)
        else:
            print(f"ERROR: Server returned status {response.status_code}")
            print(f"Response Body: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("CRITICAL ERROR: Could not connect to Ollama. Is the server running?")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    debug_ollama()

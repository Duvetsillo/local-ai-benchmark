import requests
import json

def list_models():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get('models', [])
        if not models:
            print("No models found in Ollama.")
            return []
        
        print("Installed Models:")
        for m in models:
            print(f"- {m['name']}")
        return [m['name'] for m in models]
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return []

if __name__ == "__main__":
    list_models()

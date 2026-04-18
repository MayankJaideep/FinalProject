import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("🔍 Testing API Endpoints...")
    
    # 1. Health
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {resp.status_code} - {resp.json()}")
        assert resp.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return

    # 2. Prediction
    print("\nTesting Prediction...")
    payload = {
        "description": "The case involves a dispute over a commercial lease agreement where the tenant failed to pay rent for 6 months due to force majeure events claimed during the COVID-19 pandemic.",
        "court": "Delhi High Court",
        "case_type": "Civil Commercial"
    }
    
    start = time.time()
    try:
        resp = requests.post(f"{BASE_URL}/predict", json=payload)
        print(f"Prediction Status: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()['result']
            print(f"Outcome (Advanced): {result.get('predicted_outcome')}")
            print(f"Confidence: {result.get('confidence_level')} ({result.get('confidence'):.2f})")
            print(f"Method: {result.get('method', 'Unknown')}")
            print(f"Time: {time.time() - start:.2f}s")
        else:
            print(f"❌ Prediction failed: {resp.text}")

        # Test Legacy
        print("\nTesting Legacy Prediction...")
        payload['model_version'] = 'legacy'
        start = time.time()
        resp = requests.post(f"{BASE_URL}/predict", json=payload)
        if resp.status_code == 200:
            result = resp.json()['result']
            print(f"Outcome (Legacy): {result.get('predicted_outcome')}")
            print(f"Confidence: {result.get('confidence_level')} ({result.get('confidence'):.2f})")
            print(f"Method: {result.get('method', 'Unknown')}")
            print(f"Time: {time.time() - start:.2f}s")
        else:
            print(f"❌ Legacy Prediction failed: {resp.text}")
    except Exception as e:
        print(f"❌ Prediction error: {e}")

    # 3. Chat
    print("\nTesting Chat...")
    chat_payload = {
        "message": "What are the legal precedents for force majeure in commercial leases?",
        "history": []
    }
    
    start = time.time()
    try:
        resp = requests.post(f"{BASE_URL}/chat", json=chat_payload)
        print(f"Chat Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Response Length: {len(data['response'])}")
            print(f"Sources: {len(data['sources'])}")
            print(f"Time: {time.time() - start:.2f}s")
        else:
            print(f"❌ Chat failed: {resp.text}")
    except Exception as e:
        print(f"❌ Chat error: {e}")

if __name__ == "__main__":
    test_api()

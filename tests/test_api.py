import requests
import json
from pathlib import Path

def test_sow_extraction():
    """Test the SOW extraction API"""
    
    # Configuration
    base_url = "http://localhost:8000"
    pdf_path = Path("samples/sample_manufacturing_sow.pdf")
    
    if not pdf_path.exists():
        print("ERROR: Sample PDF not found. Please ensure sample PDF exists.")
        return False
    
    try:
        # Test health endpoint
        print("Testing API health...")
        health = requests.get(f"{base_url}/health", timeout=10)
        if health.status_code != 200:
            print("ERROR: API health check failed")
            return False
        print("SUCCESS: API is healthy")
        
        # Test SOW extraction
        print("Testing SOW extraction...")
        with open(pdf_path, 'rb') as f:
            response = requests.post(
                f"{base_url}/extract-sow", 
                files={'file': f}, 
                timeout=120
            )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"SUCCESS: Extraction completed")
            print(f"- Milestones: {len(result.get('milestones', []))}")
            print(f"- Deliverables: {len(result.get('deliverables', []))}")
            print(f"- Payment terms: {len(result.get('payment_terms', []))}")
            print(f"- Confidence: {result.get('metadata', {}).get('processing_confidence', 0)}")
            
            # Save results
            with open("tests/api_test_result.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            return True
        else:
            print(f"ERROR: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to API. Start server with 'python app.py'")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("SOW AI Extraction - API Test")
    print("=" * 40)
    
    success = test_sow_extraction()
    print("\nRESULT:", "PASSED" if success else "FAILED")
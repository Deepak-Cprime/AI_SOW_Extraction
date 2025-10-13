import requests
import json
import base64
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

def test_sow_extraction_base64():
    """Test the SOW extraction API with base64 encoded PDF"""

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

        # Read and encode PDF to base64
        print("Encoding PDF to base64...")
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
            base64_content = base64.b64encode(pdf_content).decode('utf-8')

        # Test SOW extraction with base64
        print("Testing SOW extraction with base64...")
        payload = {
            "filename": pdf_path.name,
            "file_content": base64_content
        }

        response = requests.post(
            f"{base_url}/extract-sow-base64",
            json=payload,
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
            with open("tests/api_test_base64_result.json", 'w', encoding='utf-8') as f:
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

    # Test traditional file upload
    print("\n[1] Testing traditional file upload...")
    success1 = test_sow_extraction()
    print("RESULT:", "PASSED" if success1 else "FAILED")

    # Test base64 upload
    print("\n[2] Testing base64 JSON upload...")
    success2 = test_sow_extraction_base64()
    print("RESULT:", "PASSED" if success2 else "FAILED")

    print("\n" + "=" * 40)
    print("OVERALL:", "PASSED" if (success1 and success2) else "FAILED")
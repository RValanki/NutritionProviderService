"""
Local test script for Lambda handler.
Tests the handler without deploying to AWS.
"""
import json
import base64
from handler import lambda_handler


def test_text_only():
    """Test with text description only"""
    print("=" * 60)
    print("TEST 1: Text Description Only")
    print("=" * 60)
    
    event = {
        'body': json.dumps({
            'textDescription': 'I had butter chicken with basmati rice and two pieces of garlic naan'
        })
    }
    
    response = lambda_handler(event, None)
    
    print(f"Status Code: {response['statusCode']}")
    print("\nResponse Body:")
    body = json.loads(response['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    return response['statusCode'] == 200


def test_image_only():
    """Test with image only"""
    print("\n" + "=" * 60)
    print("TEST 2: Image Only")
    print("=" * 60)
    
    try:
        # Load test image
        with open('test/tacos.jpg', 'rb') as f:
            image_bytes = f.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        event = {
            'body': json.dumps({
                'imageBase64': image_base64
            })
        }
        
        response = lambda_handler(event, None)
        
        print(f"Status Code: {response['statusCode']}")
        print("\nResponse Body:")
        body = json.loads(response['body'])
        print(json.dumps(body, indent=2, ensure_ascii=False))
        
        return response['statusCode'] == 200
        
    except FileNotFoundError:
        print("❌ Test image not found: test/tacos.jpg")
        return False


def test_both_text_and_image():
    """Test with both text and image"""
    print("\n" + "=" * 60)
    print("TEST 3: Both Text and Image")
    print("=" * 60)
    
    try:
        # Load test image
        with open('test/tacos.jpg', 'rb') as f:
            image_bytes = f.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        event = {
            'body': json.dumps({
                'textDescription': 'Three birria tacos with consommé',
                'imageBase64': image_base64
            })
        }
        
        response = lambda_handler(event, None)
        
        print(f"Status Code: {response['statusCode']}")
        print("\nResponse Body:")
        body = json.loads(response['body'])
        print(json.dumps(body, indent=2, ensure_ascii=False))
        
        return response['statusCode'] == 200
        
    except FileNotFoundError:
        print("❌ Test image not found: test/tacos.jpg")
        return False


def test_no_input():
    """Test error handling - no input provided"""
    print("\n" + "=" * 60)
    print("TEST 4: Error Handling (No Input)")
    print("=" * 60)
    
    event = {
        'body': json.dumps({})
    }
    
    response = lambda_handler(event, None)
    
    print(f"Status Code: {response['statusCode']}")
    print("\nResponse Body:")
    body = json.loads(response['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    # Should return 400
    return response['statusCode'] == 400


def test_missing_body():
    """Test error handling - missing body"""
    print("\n" + "=" * 60)
    print("TEST 5: Error Handling (Missing Body)")
    print("=" * 60)
    
    event = {}
    
    response = lambda_handler(event, None)
    
    print(f"Status Code: {response['statusCode']}")
    print("\nResponse Body:")
    body = json.loads(response['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    # Should return 400
    return response['statusCode'] == 400


def test_invalid_json():
    """Test error handling - invalid JSON"""
    print("\n" + "=" * 60)
    print("TEST 6: Error Handling (Invalid JSON)")
    print("=" * 60)
    
    event = {
        'body': 'this is not valid json'
    }
    
    response = lambda_handler(event, None)
    
    print(f"Status Code: {response['statusCode']}")
    print("\nResponse Body:")
    body = json.loads(response['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    # Should return 400
    return response['statusCode'] == 400


def test_branded_product():
    """Test with a branded product"""
    print("\n" + "=" * 60)
    print("TEST 7: Branded Product")
    print("=" * 60)
    
    event = {
        'body': json.dumps({
            'textDescription': 'Musashi Shred & Burn protein shake, 375ml bottle'
        })
    }
    
    response = lambda_handler(event, None)
    
    print(f"Status Code: {response['statusCode']}")
    print("\nResponse Body:")
    body = json.loads(response['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    return response['statusCode'] == 200


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "🧪" * 30)
    print("RUNNING ALL LAMBDA HANDLER TESTS")
    print("🧪" * 30 + "\n")
    
    tests = [
        ("Text Only", test_text_only),
        ("Image Only", test_image_only),
        ("Both Text & Image", test_both_text_and_image),
        ("No Input (Error)", test_no_input),
        ("Missing Body (Error)", test_missing_body),
        ("Invalid JSON (Error)", test_invalid_json),
        ("Branded Product", test_branded_product),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed_count}/{total_count} tests passed")
    print("=" * 60)
    
    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
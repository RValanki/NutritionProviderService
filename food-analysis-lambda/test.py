"""
Test script for ClaudeVisionService - Step 1 only (Image → Claude Analysis)

This demonstrates how to use the service to analyze food from text or images.
"""
import os
import json
from service.claude_vision_service import ClaudeVisionService


def test_text_analysis():
    """Test analyzing food from text description"""
    print("=" * 60)
    print("TEST 1: Text Description Analysis")
    print("=" * 60)
    
    service = ClaudeVisionService()
    
    # Example text input
    text = "I had butter chicken with basmati rice and two pieces of garlic naan for dinner"
    
    print(f"\nInput: {text}\n")
    
    try:
        result = service.analyze_food(text_description=text)
        
        # Print raw JSON response from Claude
        print("\n" + "=" * 60)
        print("CLAUDE'S RAW JSON RESPONSE (camelCase)")
        print("=" * 60)
        print(result.raw_response)
        
        # Get final API response
        print("\n" + "=" * 60)
        print("FINAL API RESPONSE (with totals)")
        print("=" * 60)
        api_response = service.get_api_response(result)
        print(json.dumps(api_response, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {e}")


def test_branded_product():
    """Test analyzing a branded product"""
    print("\n" + "=" * 60)
    print("TEST 2: Branded Product Analysis")
    print("=" * 60)
    
    service = ClaudeVisionService()
    
    # Example branded product
    text = "Musashi Shred & Burn protein shake, 375ml bottle"
    
    print(f"\nInput: {text}\n")
    
    try:
        result = service.analyze_food(text_description=text)
        
        # Print raw JSON response from Claude
        print("\n" + "=" * 60)
        print("CLAUDE'S RAW JSON RESPONSE (camelCase)")
        print("=" * 60)
        print(result.raw_response)
        
        # Get final API response
        print("\n" + "=" * 60)
        print("FINAL API RESPONSE (with totals)")
        print("=" * 60)
        api_response = service.get_api_response(result)
        print(json.dumps(api_response, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {e}")


def test_image_analysis():
    """Test analyzing food from an image"""
    print("\n" + "=" * 60)
    print("TEST 3: Image Analysis")
    print("=" * 60)
    
    import base64
    import sys
    
    # Hardcoded image path - UPDATE THIS with your local image path
    HARDCODED_IMAGE_PATH = "/Users/rohitvalanki/NutritionProviderService/food-analysis-lambda/test/tacos.jpg"
    
    # Check if image path provided as command line argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"\nUsing image from command line: {image_path}")
    elif os.path.exists(HARDCODED_IMAGE_PATH):
        image_path = HARDCODED_IMAGE_PATH
        print(f"\nUsing hardcoded image: {image_path}")
    else:
        print("\n⚠️  No image available for testing")
        print(f"   Hardcoded path not found: {HARDCODED_IMAGE_PATH}")
        print("\nTo test with an image:")
        print("  Option 1: Update HARDCODED_IMAGE_PATH in the test script")
        print("  Option 2: Run with image path: python test_claude_vision.py /path/to/image.jpg")
        print("\nSkipping image test...")
        return
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"\n❌ Error: Image file not found at {image_path}")
        return
    
    print(f"Loading image from: {image_path}")
    
    try:
        # Load and convert image to base64
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        file_size_kb = len(image_bytes) / 1024
        print(f"✓ Image loaded successfully ({file_size_kb:.1f} KB)")
        
        # Analyze with Claude
        service = ClaudeVisionService()
        print("\nAnalyzing image with Claude Sonnet 4.5...")
        result = service.analyze_food(image_base64=image_base64)
        
        # Print raw JSON response from Claude
        print("\n" + "=" * 60)
        print("CLAUDE'S RAW JSON RESPONSE (camelCase)")
        print("=" * 60)
        print(result.raw_response)
        
        # Get final API response
        print("\n" + "=" * 60)
        print("FINAL API RESPONSE (with totals)")
        print("=" * 60)
        api_response = service.get_api_response(result)
        print(json.dumps(api_response, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    #test_text_analysis()
    #test_branded_product()
    test_image_analysis()
    
    print("\n" + "=" * 60)
    print("All tests complete!")
    print("=" * 60)
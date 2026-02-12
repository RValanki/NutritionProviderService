"""
Utility functions for the food analysis service.
"""
import base64
import json
import re
from typing import Optional, Dict, Any


def validate_base64_image(image_base64: str) -> bool:
    """
    Validate that a string is valid base64 encoded image data.
    
    Args:
        image_base64: Base64 encoded image string
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Remove data URI prefix if present
        if image_base64.startswith('data:image'):
            image_base64 = image_base64.split(',')[1]
        
        # Try to decode
        base64.b64decode(image_base64)
        return True
    except Exception:
        return False


def get_image_media_type(image_base64: str) -> str:
    """
    Extract media type from base64 image data URI, or infer from content.
    
    Args:
        image_base64: Base64 encoded image string (with or without data URI prefix)
        
    Returns:
        Media type string (e.g., 'image/jpeg', 'image/png')
    """
    # Check for data URI prefix
    if image_base64.startswith('data:image'):
        media_type = image_base64.split(';')[0].replace('data:', '')
        return media_type
    
    # Default to jpeg if no prefix
    return 'image/jpeg'


def clean_base64_image(image_base64: str) -> str:
    """
    Remove data URI prefix from base64 string if present.
    
    Args:
        image_base64: Base64 encoded image string
        
    Returns:
        Clean base64 string without prefix
    """
    if image_base64.startswith('data:image'):
        return image_base64.split(',')[1]
    return image_base64


def extract_json_from_response(text: str) -> Optional[Dict[Any, Any]]:
    """
    Extract JSON from Claude's response, handling markdown code blocks and text.
    
    Args:
        text: Raw text response from Claude
        
    Returns:
        Parsed JSON dict, or None if parsing fails
    """
    # Try to find JSON in markdown code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    
    if match:
        json_str = match.group(1)
    else:
        # Try to find raw JSON (look for outermost braces)
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            json_str = text
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def format_nutrition_value(value: Optional[float], precision: int = 1) -> Optional[float]:
    """
    Format nutrition values to consistent precision.
    
    Args:
        value: Nutrition value (can be None)
        precision: Decimal places
        
    Returns:
        Formatted value or None
    """
    if value is None:
        return None
    return round(float(value), precision)


def generate_cache_key(
    name: str,
    brand: Optional[str] = None,
    quantity: Optional[float] = None,
    unit: Optional[str] = None
) -> str:
    """
    Generate a consistent cache key for DDB lookups.
    
    Args:
        name: Food item name
        brand: Optional brand name
        quantity: Optional quantity (normalized to 100g/100ml)
        unit: Optional unit
        
    Returns:
        Cache key string
    """
    # Normalize name: lowercase, remove special chars, hyphenate spaces
    normalized_name = name.lower().strip()
    normalized_name = re.sub(r'[^\w\s-]', '', normalized_name)
    normalized_name = re.sub(r'\s+', '-', normalized_name)
    
    if brand:
        normalized_brand = brand.lower().strip().replace(' ', '-')
        key = f"NUTRITION#{normalized_brand}-{normalized_name}"
    else:
        key = f"NUTRITION#{normalized_name}"
    
    # Add quantity/unit for specific lookups
    if quantity and unit:
        key += f"-{int(quantity)}{unit}"
    
    return key


def calculate_total_nutrition(components: list) -> Dict[str, float]:
    """
    Calculate total nutrition across all components.
    
    Args:
        components: List of FoodComponent objects with nutrition data
        
    Returns:
        Dict with total nutrition values
    """
    totals = {
        'calories': 0.0,
        'protein': 0.0,
        'carbs': 0.0,
        'fat': 0.0,
        'fiber': 0.0,
        'sugar': 0.0,
        'sodium': 0.0,
    }
    
    for component in components:
        nutrition = component.nutrition or component.claude_estimate
        
        totals['calories'] += nutrition.calories
        totals['protein'] += nutrition.protein
        totals['carbs'] += nutrition.carbs
        totals['fat'] += nutrition.fat
        
        if nutrition.fiber:
            totals['fiber'] += nutrition.fiber
        if nutrition.sugar:
            totals['sugar'] += nutrition.sugar
        if nutrition.sodium:
            totals['sodium'] += nutrition.sodium
    
    # Clean up zeros for optional fields
    if totals['fiber'] == 0:
        totals['fiber'] = None
    if totals['sugar'] == 0:
        totals['sugar'] = None
    if totals['sodium'] == 0:
        totals['sodium'] = None
    
    return totals
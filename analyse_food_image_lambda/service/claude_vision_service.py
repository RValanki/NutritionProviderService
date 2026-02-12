"""
Claude Vision Service for analyzing food from images or text descriptions.
Uses Claude Sonnet 4.5 for accurate vision and nutrition analysis.
"""
import os
import json
from typing import Optional, List
from anthropic import Anthropic

from .models import (
    ClaudeAnalysisResult,
    FoodComponent,
    NutritionData,
    ItemType,
    create_nutrition_data_from_dict,
)
from .utils import (
    validate_base64_image,
    get_image_media_type,
    clean_base64_image,
    extract_json_from_response,
)


class ClaudeVisionService:
    """Service for analyzing food using Claude Sonnet 4.5"""
    
    def __init__(self):
        """Initialize the Claude client"""
        self.client = Anthropic(api_key="placeholder")
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_food(
        self,
        text_description: Optional[str] = None,
        image_base64: Optional[str] = None
    ) -> ClaudeAnalysisResult:
        """
        Analyze food from text description or image.
        
        Args:
            text_description: Text description of the food
            image_base64: Base64 encoded image
            
        Returns:
            ClaudeAnalysisResult with dish analysis and component breakdown
            
        Raises:
            ValueError: If neither text nor image provided, or if image is invalid
        """
        if not text_description and not image_base64:
            raise ValueError("Either text_description or image_base64 must be provided")
        
        # Build the prompt
        system_prompt = self._build_system_prompt()
        user_message = self._build_user_message(text_description, image_base64)
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=system_prompt,
            messages=[user_message]
        )
        
        # Extract response text
        response_text = response.content[0].text
        
        # Parse JSON response
        parsed_result = extract_json_from_response(response_text)
        
        if not parsed_result:
            raise ValueError(f"Failed to parse JSON from Claude response: {response_text[:200]}")
        
        # Convert to ClaudeAnalysisResult
        return self._parse_claude_response(parsed_result, response_text)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for Claude"""
        return """You are a nutrition analysis expert. Your task is to analyze food from images or text descriptions and provide detailed nutritional breakdowns.

For each food item or meal, you must:
1. Identify if it's a branded product (with packaging/label) or a prepared meal/dish
2. Break down the food into individual components
3. Estimate quantities for each component
4. Provide accurate calorie and macro estimates per component

CRITICAL: You must respond with ONLY valid JSON, no other text. Use this exact structure:

{
  "dish_name": "string",
  "item_type": "branded_product" | "meal" | "meal_component",
  "components": [
    {
      "name": "string",
      "item_type": "branded_product" | "meal_component",
      "brand": "string or null",
      "barcode": "string or null (if visible)",
      "quantity": number,
      "unit": "g" | "ml" | "pieces" | "slices" | "cups",
      "claude_estimate": {
        "calories": number,
        "protein": number,
        "carbs": number,
        "fat": number,
        "fiber": number or null,
        "sugar": number or null,
        "sodium": number or null
      }
    }
  ],
  "total_claude_estimate": {
    "calories": number,
    "protein": number,
    "carbs": number,
    "fat": number,
    "fiber": number or null,
    "sugar": number or null,
    "sodium": number or null
  }
}

Guidelines:
- For branded products (protein shakes, packaged foods): Set item_type to "branded_product", include brand name
- For meals (butter chicken, pasta dish): Set item_type to "meal", break into components with item_type "meal_component"
- Be specific with component names (e.g., "basmati rice" not just "rice")
- Estimate realistic portion sizes based on visual cues
- Nutrition values should be for the TOTAL quantity shown, not per 100g
- If you can see a barcode, include it
- total_claude_estimate should sum all component estimates"""
    
    def _build_user_message(
        self,
        text_description: Optional[str],
        image_base64: Optional[str]
    ) -> dict:
        """Build the user message for Claude API"""
        content = []
        
        # Add image if provided
        if image_base64:
            if not validate_base64_image(image_base64):
                raise ValueError("Invalid base64 image data")
            
            media_type = get_image_media_type(image_base64)
            clean_image = clean_base64_image(image_base64)
            
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": clean_image,
                }
            })
        
        # Add text prompt
        if text_description:
            prompt = f"Analyze this food and provide nutritional breakdown: {text_description}"
        else:
            prompt = "Analyze the food in this image and provide a detailed nutritional breakdown."
        
        content.append({
            "type": "text",
            "text": prompt
        })
        
        return {
            "role": "user",
            "content": content
        }
    
    def _parse_claude_response(
        self,
        response_json: dict,
        raw_response: str
    ) -> ClaudeAnalysisResult:
        """
        Parse Claude's JSON response into ClaudeAnalysisResult model.
        
        Args:
            response_json: Parsed JSON from Claude
            raw_response: Raw text response for debugging
            
        Returns:
            ClaudeAnalysisResult object
        """
        # Parse components
        components = []
        for comp_data in response_json.get('components', []):
            component = FoodComponent(
                name=comp_data['name'],
                item_type=ItemType(comp_data['item_type']),
                quantity=float(comp_data['quantity']),
                unit=comp_data['unit'],
                claude_estimate=create_nutrition_data_from_dict(comp_data['claude_estimate']),
                brand=comp_data.get('brand'),
                barcode=comp_data.get('barcode'),
            )
            components.append(component)
        
        # Parse total estimate
        total_estimate = create_nutrition_data_from_dict(
            response_json['total_claude_estimate']
        )
        
        return ClaudeAnalysisResult(
            dish_name=response_json['dish_name'],
            item_type=ItemType(response_json['item_type']),
            components=components,
            total_claude_estimate=total_estimate,
            raw_response=raw_response,
        )
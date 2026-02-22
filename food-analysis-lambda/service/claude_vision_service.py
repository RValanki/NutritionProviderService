"""
Claude Vision Service for analyzing food from images or text descriptions.
Uses Claude Sonnet 4.5 for vision analysis and Claude Haiku 4.5 for text-only.
Optimized for cost with minimal output tokens.
"""
import os
import json
import re
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
    """Service for analyzing food using Claude models"""
    
    def __init__(self):
        """Initialize the Claude client"""
        self.client = Anthropic(api_key="")
        self.vision_model = "claude-sonnet-4-20250514"  # For image analysis
        self.text_model = "claude-haiku-4-5-20251001"    # For text-only analysis
    
    def analyze_food(
        self,
        text_description: Optional[str] = None,
        image_base64: Optional[str] = None
    ) -> ClaudeAnalysisResult:
        """
        Analyze food from text description or image.
        Uses Haiku 4.5 for text-only (cheaper), Sonnet 4.5 for images (vision required).
        
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
        
        # Select model based on input type
        model = self.vision_model if image_base64 else self.text_model
        
        # Optimized token limits
        max_tokens = 600 if image_base64 else 800
        
        # Build the prompt
        system_prompt = self._build_system_prompt()
        user_message = self._build_user_message(text_description, image_base64)
        
        # Call Claude API with prompt caching
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
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
        """Build the system prompt for Claude - optimized for minimal tokens"""
        return """Nutrition expert. Respond ONLY with valid JSON in camelCase:

{
  "dishName": "string",
  "itemType": "branded_product"|"meal"|"meal_component",
  "components": [
    {
      "name": "string",
      "quantity": number,
      "unit": "g"|"ml"|"pieces"|"slices"|"cups",
      "caloriesPerUnit": number,
      "proteinPerUnit": number,
      "carbsPerUnit": number,
      "fatPerUnit": number
    }
  ]
}

Rules: Smart units (pieces for countable, grams for bulk). PerUnit = per 1g or per 1 piece. Major components only (3-5 max). Round to 1 decimal. Component names should be simple food names without parentheses or brackets."""
    
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
        
        # Add text prompt - simplified
        if text_description:
            prompt = f"Analyze: {text_description}"
        else:
            prompt = "Analyze this food."
        
        content.append({
            "type": "text",
            "text": prompt
        })
        
        return {
            "role": "user",
            "content": content
        }
    
    def _clean_component_name(self, name: str) -> str:
        """
        Clean component name to remove parentheses, brackets, and other non-essential characters.
        Examples:
        - "Shredded beef (birria)" -> "Shredded beef birria"
        - "White onion (diced)" -> "White onion diced"
        - "Oaxaca cheese" -> "Oaxaca cheese"
        """
        # Remove parentheses and brackets but keep the content
        name = re.sub(r'[(\[\{]', '', name)
        name = re.sub(r'[)\]\}]', '', name)
        
        # Clean up extra spaces
        name = ' '.join(name.split())
        
        # Capitalize first letter
        name = name.strip().capitalize()
        
        return name
    
    def _parse_claude_response(
        self,
        response_json: dict,
        raw_response: str
    ) -> ClaudeAnalysisResult:
        """
        Parse Claude's JSON response into ClaudeAnalysisResult model.
        Claude returns per-unit nutrition in camelCase, we calculate totals here.
        
        Args:
            response_json: Parsed JSON from Claude (in camelCase)
            raw_response: Raw text response for debugging
            
        Returns:
            ClaudeAnalysisResult object with both per-unit and total nutrition
        """
        # Parse components and calculate totals in Python
        components = []
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for comp_data in response_json.get('components', []):
            quantity = float(comp_data['quantity'])
            
            # Clean component name
            clean_name = self._clean_component_name(comp_data['name'])
            
            # Store per-unit nutrition (as returned by Claude in camelCase)
            per_unit_nutrition = NutritionData(
                calories=float(comp_data['caloriesPerUnit']),
                protein=float(comp_data['proteinPerUnit']),
                carbs=float(comp_data['carbsPerUnit']),
                fat=float(comp_data['fatPerUnit']),
            )
            
            # Calculate total macros: per_unit × quantity
            comp_calories = round(per_unit_nutrition.calories * quantity)
            comp_protein = round(per_unit_nutrition.protein * quantity)
            comp_carbs = round(per_unit_nutrition.carbs * quantity)
            comp_fat = round(per_unit_nutrition.fat * quantity)
            
            # Create total nutrition data
            total_nutrition = NutritionData(
                calories=comp_calories,
                protein=comp_protein,
                carbs=comp_carbs,
                fat=comp_fat,
            )
            
            component = FoodComponent(
                name=clean_name,  # Use cleaned name
                item_type=ItemType.MEAL_COMPONENT,
                quantity=quantity,
                unit=comp_data['unit'],
                per_unit_nutrition=per_unit_nutrition,  # Store per-unit
                claude_estimate=total_nutrition,         # Store total
                brand=None,
                barcode=None,
            )
            components.append(component)
            
            # Sum up for total
            total_calories += comp_calories
            total_protein += comp_protein
            total_carbs += comp_carbs
            total_fat += comp_fat
        
        # Create total estimate from summed components
        total_estimate = NutritionData(
            calories=total_calories,
            protein=total_protein,
            carbs=total_carbs,
            fat=total_fat,
        )
        
        return ClaudeAnalysisResult(
            dish_name=response_json['dishName'],
            item_type=ItemType(response_json['itemType']),
            components=components,
            total_claude_estimate=total_estimate,
            raw_response=raw_response,
        )
    
    def get_api_response(self, result: ClaudeAnalysisResult) -> dict:
        """
        Convert ClaudeAnalysisResult to the final API response format (camelCase).
        This matches what Claude returns, plus the calculated totals.
        
        Args:
            result: ClaudeAnalysisResult from analyze_food()
            
        Returns:
            Dict in camelCase format ready for API response
        """
        return {
            "dishName": result.dish_name,
            "itemType": result.item_type.value,
            "components": [
                {
                    "name": comp.name,
                    "quantity": comp.quantity,
                    "unit": comp.unit,
                    "perUnitNutrition": {
                        "calories": comp.per_unit_nutrition.calories,
                        "protein": comp.per_unit_nutrition.protein,
                        "carbs": comp.per_unit_nutrition.carbs,
                        "fat": comp.per_unit_nutrition.fat,
                    },
                    "nutrition": {
                        "calories": comp.claude_estimate.calories,
                        "protein": comp.claude_estimate.protein,
                        "carbs": comp.claude_estimate.carbs,
                        "fat": comp.claude_estimate.fat,
                    }
                }
                for comp in result.components
            ],
            "totalNutrition": {
                "calories": result.total_claude_estimate.calories,
                "protein": result.total_claude_estimate.protein,
                "carbs": result.total_claude_estimate.carbs,
                "fat": result.total_claude_estimate.fat,
            }
        }
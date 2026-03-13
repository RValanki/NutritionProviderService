"""
Claude Amend Service for modifying an existing meal analysis based on amendment text.
Uses Claude Haiku 4.5 (text-only, no vision needed).
"""
import os
import json
from anthropic import Anthropic

from .models import (
    ClaudeAnalysisResult,
    FoodComponent,
    NutritionData,
    ItemType,
)
from .utils import extract_json_from_response


class ClaudeAmendService:
    """Service for amending an existing meal breakdown using Claude"""

    def __init__(self):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-haiku-4-5-20251001"

    def amend_meal(
        self,
        existing_meal: dict,
        amendment_text: str,
    ) -> ClaudeAnalysisResult:
        """
        Amend an existing meal analysis based on user-provided amendment text.

        Args:
            existing_meal: The current API response dict (dishName, components, totalNutrition)
            amendment_text: Free-text amendment e.g. "add 50g rice" or "the lamb is actually chicken"

        Returns:
            ClaudeAnalysisResult with updated breakdown
        """
        system_prompt = self._build_system_prompt()
        user_message = self._build_user_message(existing_meal, amendment_text)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=800,
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[user_message]
        )

        response_text = response.content[0].text
        parsed_result = extract_json_from_response(response_text)

        if not parsed_result:
            raise ValueError(f"Failed to parse JSON from Claude response: {response_text[:200]}")

        return self._parse_response(parsed_result, response_text)

    def _build_system_prompt(self) -> str:
        return """Nutrition expert. You will receive an existing meal breakdown and an amendment instruction.
Apply the amendment to the breakdown and respond ONLY with valid JSON in camelCase:

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

Rules:
- Keep existing components unchanged unless the amendment affects them
- Add new components if the amendment introduces new ingredients
- Remove or replace components only if explicitly instructed
- PerUnit = per 1g or per 1 piece
- Round to 1 decimal
- Component names should be simple food names without parentheses or brackets
- Return ALL components (existing + amended), not just the changed ones"""

    def _build_user_message(self, existing_meal: dict, amendment_text: str) -> dict:
        existing_summary = json.dumps({
            "dishName": existing_meal.get("dishName"),
            "components": [
                {
                    "name": c["name"],
                    "quantity": c["quantity"],
                    "unit": c["unit"],
                    "perUnitNutrition": c.get("perUnitNutrition", {}),
                }
                for c in existing_meal.get("components", [])
            ]
        }, ensure_ascii=False)

        return {
            "role": "user",
            "content": (
                f"Existing meal:\n{existing_summary}\n\n"
                f"Amendment: {amendment_text}"
            )
        }

    def _parse_response(self, response_json: dict, raw_response: str) -> ClaudeAnalysisResult:
        """Same parsing logic as ClaudeVisionService._parse_claude_response"""
        import re

        def clean_name(name: str) -> str:
            name = re.sub(r'[(\[\{]', '', name)
            name = re.sub(r'[)\]\}]', '', name)
            return ' '.join(name.split()).strip().capitalize()

        components = []
        total_calories = total_protein = total_carbs = total_fat = 0

        for comp_data in response_json.get("components", []):
            quantity = float(comp_data["quantity"])

            per_unit = NutritionData(
                calories=float(comp_data["caloriesPerUnit"]),
                protein=float(comp_data["proteinPerUnit"]),
                carbs=float(comp_data["carbsPerUnit"]),
                fat=float(comp_data["fatPerUnit"]),
            )

            total_nutrition = NutritionData(
                calories=round(per_unit.calories * quantity),
                protein=round(per_unit.protein * quantity),
                carbs=round(per_unit.carbs * quantity),
                fat=round(per_unit.fat * quantity),
            )

            components.append(FoodComponent(
                name=clean_name(comp_data["name"]),
                item_type=ItemType.MEAL_COMPONENT,
                quantity=quantity,
                unit=comp_data["unit"],
                per_unit_nutrition=per_unit,
                claude_estimate=total_nutrition,
                brand=None,
                barcode=None,
            ))

            total_calories += total_nutrition.calories
            total_protein += total_nutrition.protein
            total_carbs += total_nutrition.carbs
            total_fat += total_nutrition.fat

        return ClaudeAnalysisResult(
            dish_name=response_json["dishName"],
            item_type=ItemType(response_json["itemType"]),
            components=components,
            total_claude_estimate=NutritionData(
                calories=total_calories,
                protein=total_protein,
                carbs=total_carbs,
                fat=total_fat,
            ),
            raw_response=raw_response,
        )

    def get_api_response(self, result: ClaudeAnalysisResult) -> dict:
        """Same response shape as ClaudeVisionService.get_api_response"""
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
"""
Fetches a product from Open Food Facts and maps it to the FoodComponent model.
"""
import requests
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'food-analysis-lambda'))

from service.models import (
    FoodComponent, NutritionData, ItemType, NutritionSource, ConfidenceLevel
)


OFF_API_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}"

HEADERS = {
    "User-Agent": "FoodAnalysisApp/1.0 (contact@example.com)"
}


def fetch_product(barcode: str) -> dict:
    """Fetch raw product data from Open Food Facts."""
    url = OFF_API_URL.format(barcode=barcode)
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != 1:
        raise ValueError(f"Product not found for barcode: {barcode}")

    return data["product"]


def extract_nutrition(nutriments: dict, per: str = "100g") -> NutritionData:
    """
    Extract core macros from the nutriments dict.
    per: '100g' or 'serving'
    """
    suffix = "_100g" if per == "100g" else "_serving"
    return NutritionData(
        calories=float(nutriments.get(f"energy-kcal{suffix}") or nutriments.get("energy-kcal_100g") or 0),
        protein=float(nutriments.get(f"proteins{suffix}") or 0),
        carbs=float(nutriments.get(f"carbohydrates{suffix}") or 0),
        fat=float(nutriments.get(f"fat{suffix}") or 0),
    )


def map_product_to_food_component(product: dict) -> FoodComponent:
    """Map an Open Food Facts product dict to a FoodComponent."""
    nutriments = product.get("nutriments", {})

    # Per 100g/ml nutrition (used as per_unit_nutrition)
    per_100_nutrition = extract_nutrition(nutriments, per="100g")

    # Per serving nutrition (used as the resolved nutrition)
    serving_qty = float(product.get("serving_quantity") or 100)
    serving_unit = product.get("serving_quantity_unit") or "g"

    has_serving_data = "energy-kcal_serving" in nutriments
    if has_serving_data:
        serving_nutrition = extract_nutrition(nutriments, per="serving")
    else:
        # Fall back to scaling 100g values by serving size
        scale = serving_qty / 100
        serving_nutrition = NutritionData(
            calories=per_100_nutrition.calories * scale,
            protein=per_100_nutrition.protein * scale,
            carbs=per_100_nutrition.carbs * scale,
            fat=per_100_nutrition.fat * scale,
        )

    return FoodComponent(
        name=product.get("product_name") or "Unknown Product",
        item_type=ItemType.BRANDED_PRODUCT,
        quantity=serving_qty,
        unit=serving_unit,
        per_unit_nutrition=per_100_nutrition,   # Per 100g/ml
        claude_estimate=serving_nutrition,       # Best guess at serving total
        brand=product.get("brands"),
        barcode=product.get("code"),
        nutrition=serving_nutrition,
        source=NutritionSource.OPEN_FOOD_FACTS,
        confidence=ConfidenceLevel.HIGH,
    )


def get_food_component(barcode: str) -> FoodComponent:
    """Main entry point: fetch + map a barcode to FoodComponent."""
    product = fetch_product(barcode)
    return map_product_to_food_component(product)


if __name__ == "__main__":
    barcode = "9300675087018"
    component = get_food_component(barcode)

    print(f"Name:       {component.name}")
    print(f"Brand:      {component.brand}")
    print(f"Barcode:    {component.barcode}")
    print(f"Type:       {component.item_type}")
    print(f"Serving:    {component.quantity}{component.unit}")
    print(f"Source:     {component.source}")
    print(f"Confidence: {component.confidence}")
    print()
    print("--- Nutrition per 100g/ml ---")
    print(f"  Calories: {component.per_unit_nutrition.calories} kcal")
    print(f"  Protein:  {component.per_unit_nutrition.protein}g")
    print(f"  Carbs:    {component.per_unit_nutrition.carbs}g")
    print(f"  Fat:      {component.per_unit_nutrition.fat}g")
    print()
    print(f"--- Nutrition per serving ({component.quantity}{component.unit}) ---")
    print(f"  Calories: {component.nutrition.calories} kcal")
    print(f"  Protein:  {component.nutrition.protein}g")
    print(f"  Carbs:    {component.nutrition.carbs}g")
    print(f"  Fat:      {component.nutrition.fat}g")
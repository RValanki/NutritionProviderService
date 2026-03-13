"""
Local test script for the /amend-food Lambda handler.
Simulates an API Gateway event and prompts for amendment text via CLI.
"""
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Add project root to path so service imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from amend_handler import lambda_handler

# -------------------------
# Test payload — mirrors a real FoodAnalysisResponse
# -------------------------
TEST_MEAL = {
    "dishName": "Grilled Chicken Salad",
    "itemType": "meal",
    "components": [
        {
            "name": "Chicken breast",
            "quantity": 150,
            "unit": "g",
            "perUnitNutrition": {
                "calories": 1.65,
                "protein": 0.31,
                "carbs": 0.0,
                "fat": 0.04
            },
            "nutrition": {
                "calories": 248,
                "protein": 47,
                "carbs": 0,
                "fat": 6
            }
        },
        {
            "name": "Mixed greens",
            "quantity": 80,
            "unit": "g",
            "perUnitNutrition": {
                "calories": 0.2,
                "protein": 0.02,
                "carbs": 0.03,
                "fat": 0.0
            },
            "nutrition": {
                "calories": 16,
                "protein": 2,
                "carbs": 2,
                "fat": 0
            }
        },
        {
            "name": "Cherry tomatoes",
            "quantity": 60,
            "unit": "g",
            "perUnitNutrition": {
                "calories": 0.18,
                "protein": 0.009,
                "carbs": 0.039,
                "fat": 0.002
            },
            "nutrition": {
                "calories": 11,
                "protein": 1,
                "carbs": 2,
                "fat": 0
            }
        },
        {
            "name": "Olive oil dressing",
            "quantity": 15,
            "unit": "ml",
            "perUnitNutrition": {
                "calories": 8.84,
                "protein": 0.0,
                "carbs": 0.0,
                "fat": 1.0
            },
            "nutrition": {
                "calories": 133,
                "protein": 0,
                "carbs": 0,
                "fat": 15
            }
        }
    ],
    "totalNutrition": {
        "calories": 408,
        "protein": 50,
        "carbs": 4,
        "fat": 21
    }
}

TEST_USER_ID = "test-user-123"


def build_event(amendment_text: str) -> dict:
    """Wrap payload in an API Gateway-style event."""
    return {
        "body": json.dumps({
            "userId": TEST_USER_ID,
            "existingMeal": TEST_MEAL,
            "amendmentText": amendment_text,
        })
    }


def print_response(response: dict):
    """Pretty-print the Lambda response."""
    status = response.get("statusCode")
    body = json.loads(response.get("body", "{}"))

    print(f"\n{'='*50}")
    print(f"Status: {status}")
    print(f"{'='*50}")

    if status != 200:
        print(f"❌ Error: {body.get('error')}")
        return

    print(f"🍽  Dish: {body['dishName']}")
    print(f"📊 Total Nutrition:")
    totals = body["totalNutrition"]
    print(f"   Calories : {totals['calories']} kcal")
    print(f"   Protein  : {totals['protein']}g")
    print(f"   Carbs    : {totals['carbs']}g")
    print(f"   Fat      : {totals['fat']}g")

    print(f"\n🥗 Components ({len(body['components'])}):")
    for comp in body["components"]:
        print(f"   • {comp['name']} — {comp['quantity']}{comp['unit']}"
              f"  ({comp['nutrition']['calories']} kcal, "
              f"P:{comp['nutrition']['protein']}g "
              f"C:{comp['nutrition']['carbs']}g "
              f"F:{comp['nutrition']['fat']}g)")

    print(f"{'='*50}\n")


def main():
    print("\n🧪 Amend Food — Local Test")
    print("─" * 50)
    print("Base meal: Grilled Chicken Salad")
    print("  • Chicken breast  150g  — 248 kcal")
    print("  • Mixed greens     80g  —  16 kcal")
    print("  • Cherry tomatoes  60g  —  11 kcal")
    print("  • Olive oil dress  15ml — 133 kcal")
    print(f"  Total: 408 kcal  P:50g  C:4g  F:21g")
    print("─" * 50)

    while True:
        try:
            amendment = input("\n✏️  Enter amendment (or 'q' to quit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if amendment.lower() in ("q", "quit", "exit"):
            print("Exiting.")
            break

        if not amendment:
            print("⚠️  Amendment cannot be empty.")
            continue

        print(f"\n⏳ Sending to amend_handler...")
        event = build_event(amendment)
        response = lambda_handler(event, context=None)
        print_response(response)


if __name__ == "__main__":
    main()
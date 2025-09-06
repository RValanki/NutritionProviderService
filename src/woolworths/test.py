import os
import openai
import json
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define Pydantic models
class MacroValues(BaseModel):
    calories_kcal: Optional[float]
    protein_g: Optional[float]
    fat_g: Optional[float]
    carbs_g: Optional[float]

class NutritionInfo(BaseModel):
    product_name: str
    source: str
    serving_size_g: Optional[float]
    per_100g: MacroValues
    per_serving: MacroValues
    estimated: bool

def get_nutrition_info(product_name: str) -> NutritionInfo:
    """
    Given a product name, fetch structured nutritional information
    using OpenAI API and return it as a NutritionInfo object.
    """
    prompt = f"""
I want you to act as a structured data assistant for nutritional information. I will give you a product name. For that product, do the following step by step:
\t0.\tClean the product name by removing any prefixes like “WW” or unnecessary text.
\t0.\tSearch the Woolworths website first for the product’s nutrition information.
\t0.\tIf the product is not found on Woolworths, search trusted nutrition sources such as FatSecret or CalorieKing.
\t0.\tIf it is still unavailable, search the general web for nutrition information.
Required nutritional fields (both per 100g and per serving):
\t•\tCalories (kcal)
\t•\tProtein (g)
\t•\tTotal Fat (g)
\t•\tCarbohydrates (g)
Output format: JSON with the following structure and nothing else:
{{
"product_name": "Cleaned product name",
"source": "source where information was found (e.g., Woolworths, FatSecret, Estimated from web)",
"serving_size_g": number,
"per_100g": {{
    "calories_kcal": number,
    "protein_g": number,
    "fat_g": number,
    "carbs_g": number
}},
"per_serving": {{
    "calories_kcal": number,
    "protein_g": number,
    "fat_g": number,
    "carbs_g": number
}},
"estimated": true/false
}}
Important: Only output the JSON. Do not include any explanations, commentary, or extra text. If a value is unavailable, mark it as null and set "estimated": true.
Here is the product name: {product_name}
"""

    # Call OpenAI API
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract and parse JSON
    json_output = response.choices[0].message.content
    parsed = json.loads(json_output)

    # Validate + return structured object
    return NutritionInfo(**parsed)

# Example usage:
if __name__ == "__main__":
    product_info = get_nutrition_info("Beef Porterhouse Steak & Butter 400g")
    print(product_info.json(indent=2))

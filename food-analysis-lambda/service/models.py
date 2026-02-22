"""
Data models for food analysis and nutrition tracking.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict


# -------------------------
# Enums
# -------------------------

class ItemType(str, Enum):
    """Type of food item"""
    BRANDED_PRODUCT = "branded_product"
    MEAL = "meal"
    MEAL_COMPONENT = "meal_component"


class NutritionSource(str, Enum):
    """Source of nutrition data"""
    OPEN_FOOD_FACTS = "open_food_facts"
    USDA = "usda"
    DDB_CACHE = "ddb_cache"
    AI_ESTIMATE = "ai_estimate"


class ConfidenceLevel(str, Enum):
    """Confidence in nutrition data accuracy"""
    HIGH = "high"      # From API with exact match
    MEDIUM = "medium"  # From API with fuzzy match or DDB cache
    LOW = "low"        # From Claude estimate only


# -------------------------
# Internal dataclasses
# -------------------------

@dataclass
class NutritionData:
    """Nutrition information for a food item - core macros only"""
    calories: float
    protein: float
    carbs: float
    fat: float


@dataclass
class FoodComponent:
    """Individual component of a meal or standalone food item"""
    name: str
    item_type: ItemType
    quantity: float
    unit: str
    per_unit_nutrition: NutritionData  # Per 1g or per 1 piece
    claude_estimate: NutritionData     # Total for the quantity
    
    # Optional fields
    brand: Optional[str] = None
    barcode: Optional[str] = None
    
    # Resolved nutrition (populated after API lookup)
    nutrition: Optional[NutritionData] = None
    source: Optional[NutritionSource] = None
    confidence: Optional[ConfidenceLevel] = None


@dataclass
class ClaudeAnalysisResult:
    """Result from Claude initial analysis"""
    dish_name: str
    item_type: ItemType
    components: List[FoodComponent]
    total_claude_estimate: NutritionData
    raw_response: Optional[str] = None  # For debugging


# -------------------------
# Helper functions
# -------------------------

def create_nutrition_data_from_dict(data: dict) -> NutritionData:
    """Create NutritionData from dictionary"""
    return NutritionData(
        calories=float(data.get('calories', 0)),
        protein=float(data.get('protein', 0)),
        carbs=float(data.get('carbs', 0)),
        fat=float(data.get('fat', 0)),
    )


def create_food_component_from_dict(data: dict) -> FoodComponent:
    """Create FoodComponent from dictionary"""
    return FoodComponent(
        name=data['name'],
        item_type=ItemType(data['item_type']),
        quantity=float(data['quantity']),
        unit=data['unit'],
        per_unit_nutrition=create_nutrition_data_from_dict(data['per_unit_nutrition']),
        claude_estimate=create_nutrition_data_from_dict(data['claude_estimate']),
        brand=data.get('brand'),
        barcode=data.get('barcode'),
        nutrition=create_nutrition_data_from_dict(data['nutrition']) if data.get('nutrition') else None,
        source=NutritionSource(data['source']) if data.get('source') else None,
        confidence=ConfidenceLevel(data['confidence']) if data.get('confidence') else None,
    )
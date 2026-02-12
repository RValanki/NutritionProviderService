"""
Data models for food analysis and nutrition tracking.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from typing import Literal


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
    """Nutrition information for a food item"""
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None


@dataclass
class FoodComponent:
    """Individual component of a meal or standalone food item"""
    name: str
    item_type: ItemType
    quantity: float
    unit: str
    claude_estimate: NutritionData
    
    # Optional fields
    brand: Optional[str] = None
    barcode: Optional[str] = None
    
    # Resolved nutrition (populated after API lookup)
    nutrition: Optional[NutritionData] = None
    source: Optional[NutritionSource] = None
    confidence: Optional[ConfidenceLevel] = None


@dataclass
class ClaudeAnalysisResult:
    """Result from Claude Sonnet 4.5 initial analysis"""
    dish_name: str
    item_type: ItemType
    components: List[FoodComponent]
    total_claude_estimate: NutritionData
    raw_response: Optional[str] = None  # For debugging


# -------------------------
# Pydantic models (API)
# -------------------------

class NutritionDataResponseModel(BaseModel):
    """Nutrition information response"""
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None


class FoodComponentResponseModel(BaseModel):
    """Individual food component response"""
    name: str
    item_type: Literal["branded_product", "meal", "meal_component"]
    quantity: float
    unit: str
    claude_estimate: NutritionDataResponseModel
    brand: Optional[str] = None
    barcode: Optional[str] = None
    nutrition: Optional[NutritionDataResponseModel] = None
    source: Optional[Literal["open_food_facts", "usda", "ddb_cache", "claude_estimate"]] = None
    confidence: Optional[Literal["high", "medium", "low"]] = None


class FoodAnalysisResponseModel(BaseModel):
    """Final consolidated response returned to client"""
    dish_name: str
    item_type: Literal["branded_product", "meal", "meal_component"]
    components: List[FoodComponentResponseModel]
    totals: NutritionDataResponseModel
    overall_confidence: Literal["high", "medium", "low"]
    source_breakdown: Dict[str, int] = Field(
        ..., 
        description="Count of components by source, e.g. {'open_food_facts': 2, 'claude_estimate': 1}"
    )
    cache_hit: bool = False
    processing_time_ms: Optional[float] = None


class AnalyseFoodRequestModel(BaseModel):
    """Request payload for analyse_food_image_lambda"""
    text_description: Optional[str] = None
    image_base64: Optional[str] = None
    user_id: Optional[str] = None
    meal_type: Optional[Literal["breakfast", "lunch", "dinner", "snack"]] = None
    timestamp: Optional[str] = None


# -------------------------
# Helper functions
# -------------------------

def nutrition_data_to_response(data: NutritionData) -> NutritionDataResponseModel:
    """Convert internal NutritionData to response model"""
    return NutritionDataResponseModel(
        calories=data.calories,
        protein=data.protein,
        carbs=data.carbs,
        fat=data.fat,
        fiber=data.fiber,
        sugar=data.sugar,
        sodium=data.sodium,
    )


def food_component_to_response(component: FoodComponent) -> FoodComponentResponseModel:
    """Convert internal FoodComponent to response model"""
    return FoodComponentResponseModel(
        name=component.name,
        item_type=component.item_type.value,
        quantity=component.quantity,
        unit=component.unit,
        claude_estimate=nutrition_data_to_response(component.claude_estimate),
        brand=component.brand,
        barcode=component.barcode,
        nutrition=nutrition_data_to_response(component.nutrition) if component.nutrition else None,
        source=component.source.value if component.source else None,
        confidence=component.confidence.value if component.confidence else None,
    )


def create_nutrition_data_from_dict(data: dict) -> NutritionData:
    """Create NutritionData from dictionary"""
    return NutritionData(
        calories=float(data.get('calories', 0)),
        protein=float(data.get('protein', 0)),
        carbs=float(data.get('carbs', 0)),
        fat=float(data.get('fat', 0)),
        fiber=float(data['fiber']) if data.get('fiber') else None,
        sugar=float(data['sugar']) if data.get('sugar') else None,
        sodium=float(data['sodium']) if data.get('sodium') else None,
    )


def create_food_component_from_dict(data: dict) -> FoodComponent:
    """Create FoodComponent from dictionary"""
    return FoodComponent(
        name=data['name'],
        item_type=ItemType(data['item_type']),
        quantity=float(data['quantity']),
        unit=data['unit'],
        claude_estimate=create_nutrition_data_from_dict(data['claude_estimate']),
        brand=data.get('brand'),
        barcode=data.get('barcode'),
        nutrition=create_nutrition_data_from_dict(data['nutrition']) if data.get('nutrition') else None,
        source=NutritionSource(data['source']) if data.get('source') else None,
        confidence=ConfidenceLevel(data['confidence']) if data.get('confidence') else None,
    )
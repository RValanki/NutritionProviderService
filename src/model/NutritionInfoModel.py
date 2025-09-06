from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel
from src.model.MacroValuesModel import MacroValues

class NutritionInfo(BaseModel):
    product_name: str
    source: str
    serving_size_g: Optional[float]
    per_100g: MacroValues
    per_serving: MacroValues
    estimated: bool
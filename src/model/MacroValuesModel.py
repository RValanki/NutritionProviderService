from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel

class MacroValues(BaseModel):
    calories_kcal: Optional[float]
    protein_g: Optional[float]
    fat_g: Optional[float]
    carbs_g: Optional[float]
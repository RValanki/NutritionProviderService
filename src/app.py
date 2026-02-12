from fastapi import FastAPI, HTTPException, Query
from typing import List
from concurrent.futures import ThreadPoolExecutor
import asyncio

from src.woolworths.nutrition_provider import get_nutrition_info, NutritionInfo

app = FastAPI(title="Nutrition Provider API")


@app.get("/woolworths/nutrition/", response_model=NutritionInfo)
async def fetch_nutrition(product_name: str = Query(...)):
    try:
        print("Fetching nutrition for:", product_name)
        nutrition = get_nutrition_info(product_name)
        print("Nutrition object:", nutrition)
        return nutrition.dict()
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/woolworths/nutrition/batch/")
async def fetch_nutrition_batch(products: List[str] = Query(..., description="List of product names")):
    try:
        print("Fetching batch nutrition for products:", products)
        results = []

        # Use ThreadPoolExecutor to run synchronous function concurrently
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=5) as executor:
            tasks = [loop.run_in_executor(executor, get_nutrition_info, product) for product in products]
            batch_results = await asyncio.gather(*tasks)

        # Convert results to dicts for JSON serialization
        for product_name, nutrition in zip(products, batch_results):
            print(f"Nutrition object for {product_name}:", nutrition)
            results.append({"product_name": product_name, "nutrition": nutrition.dict()})

        return results
    except Exception as e:
        print("Error in batch request:", e)
        raise HTTPException(status_code=500, detail=str(e))

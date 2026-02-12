# batch_test.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

# Import the function from your main module
from .nutrition_provider import get_nutrition_info  # adjust if your file name is different

# List of products to test
products = [
    "Beef Porterhouse Steak & Butter 400g",
    "Beechworth Bee CauseBush Honey",
    "WW Wholemeal Bread 700g",
    "Almond Milk Unsweetened 1L",
]

async def fetch_product(executor, product_name):
    loop = asyncio.get_event_loop()
    # Run the synchronous function in a separate thread
    result = await loop.run_in_executor(executor, get_nutrition_info, product_name)
    return result

async def main():
    # Use ThreadPoolExecutor to run multiple requests concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [fetch_product(executor, product) for product in products]
        results = await asyncio.gather(*tasks)

    # Print results
    for product_name, data in zip(products, results):
        print(f"=== {product_name} ===")
        # Convert Pydantic object to dict before dumping to JSON
        print(json.dumps(data.dict(), indent=2))

if __name__ == "__main__":
    asyncio.run(main())

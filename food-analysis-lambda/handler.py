"""
AWS Lambda handler for food analysis API.
Analyzes food from images or text descriptions and returns nutritional information.
"""
import json
import traceback
from typing import Dict, Any

from service.claude_vision_service import ClaudeVisionService
from service.firestore_service import write_logged_meal_event

# Initialize service at module level for Lambda container reuse
vision_service = ClaudeVisionService()


def _authenticated_uid(event: Dict[str, Any]) -> str | None:
    """The verified Firebase uid the gateway authorizer injected into the request
    context. This is the source of truth for identity — not the request body — so
    a client can't act as another user by supplying a different userId. Returns
    None when it's absent (the authorizer should always populate it for this route)."""
    ctx = (event or {}).get("requestContext", {}) or {}
    authorizer = ctx.get("authorizer", {}) or {}
    uid = authorizer.get("uid")
    if uid:
        return uid
    claims = authorizer.get("claims", {}) or {}
    return claims.get("uid") or claims.get("sub")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for food analysis.
    
    Expected input (API Gateway event):
    {
        "body": {
            "userId": "firebase-user-id",
            "textDescription": "optional text description",
            "imageBase64": "optional base64 image"
        }
    }
    """
    try:
        # 1️⃣ Parse request body
        body = event.get("body")
        if body is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No request body"})
            }

        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid JSON in request body"})
                }

        # 2️⃣ Extract inputs. Identity comes from the verified token (authorizer
        # context) first; the body userId is a deprecated fallback kept only while
        # older clients still send it.
        user_id = _authenticated_uid(event) or body.get("userId")
        text_description = body.get("textDescription")
        image_base64 = body.get("imageBase64")
        request_id = body.get("requestId")

        # 3️⃣ Validate inputs
        if not user_id:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Unauthorized"})
            }

        if not text_description and not image_base64:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": "Either textDescription or imageBase64 must be provided"
                })
            }

        # 4️⃣ Analyze food with Claude
        result = vision_service.analyze_food(
            text_description=text_description,
            image_base64=image_base64
        )

        # 5️⃣ Convert to API response format
        api_response = vision_service.get_api_response(result)

        # 6️⃣ Write loggedMeal event to Firestore
        write_logged_meal_event(user_id=user_id, meal_data=api_response, request_id=request_id)

        # 7️⃣ Return success response
        return {
            "statusCode": 200,
            "body": json.dumps(api_response, ensure_ascii=False),
        }

    except ValueError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)}),
        }

    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
        }
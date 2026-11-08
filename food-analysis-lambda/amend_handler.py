"""
AWS Lambda handler for the /amend-food endpoint.
Accepts an existing meal breakdown + amendment text, returns revised breakdown.
Writes a loggedMeal Firestore event so the Swift client picks it up via the existing listener.
"""
import json
import traceback
from typing import Dict, Any

from service.claude_amend_service import ClaudeAmendService
from service.firestore_service import write_logged_meal_event

amend_service = ClaudeAmendService()


def _authenticated_uid(event: Dict[str, Any]) -> str | None:
    """The verified Firebase uid the gateway authorizer injected into the request
    context — the source of truth for identity, not the request body."""
    ctx = (event or {}).get("requestContext", {}) or {}
    authorizer = ctx.get("authorizer", {}) or {}
    uid = authorizer.get("uid")
    if uid:
        return uid
    claims = authorizer.get("claims", {}) or {}
    return claims.get("uid") or claims.get("sub")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Expected input:
    {
        "userId": "firebase-user-id",
        "existingMeal": { ...FoodAnalysisResponse... },
        "amendmentText": "add 50g rice"
    }
    """
    try:
        body = event.get("body")
        if body is None:
            return _error(400, "No request body")

        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                return _error(400, "Invalid JSON in request body")

        # Identity from the verified token (authorizer context) first; body userId
        # is a deprecated fallback for older clients.
        user_id = _authenticated_uid(event) or body.get("userId")
        existing_meal = body.get("existingMeal")
        amendment_text = body.get("amendmentText", "").strip()
        request_id = body.get("requestId")

        if not user_id:
            return _error(401, "Unauthorized")
        if not existing_meal:
            return _error(400, "existingMeal is required")
        if not amendment_text:
            return _error(400, "amendmentText is required")

        result = amend_service.amend_meal(
            existing_meal=existing_meal,
            amendment_text=amendment_text,
        )

        api_response = amend_service.get_api_response(result)

        # Write Firestore event — Swift client picks this up via the existing
        # loggedMeal listener, same as the /analyze-food flow
        write_logged_meal_event(user_id=user_id, meal_data=api_response, request_id=request_id)

        return {
            "statusCode": 200,
            "body": json.dumps(api_response, ensure_ascii=False),
        }

    except ValueError as e:
        return _error(400, str(e))

    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        return _error(500, "Internal server error")


def _error(status: int, message: str) -> Dict[str, Any]:
    return {
        "statusCode": status,
        "body": json.dumps({"error": message}),
    }
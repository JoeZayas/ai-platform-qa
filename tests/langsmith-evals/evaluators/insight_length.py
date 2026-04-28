def evaluate_insight_length(output: str) -> dict:
    """
    Evaluator that checks if insight is between 100-600 characters.
    Returns a score from 0-1 and key boolean.
    """
    if not output:
        return {"score": 0, "key": False, "reason": "Empty insight"}

    length = len(output)

    if length < 100:
        return {
            "score": 0,
            "key": False,
            "reason": f"Insight too short ({length} chars, need >= 100)"
        }

    if length > 600:
        return {
            "score": 0.5,
            "key": True,
            "reason": f"Insight exceeds recommended length ({length} chars, recommended <= 600)"
        }

    return {
        "score": 1,
        "key": True,
        "reason": f"Insight length perfect ({length} chars)"
    }

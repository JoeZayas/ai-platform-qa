def evaluate_professional_tone(output: str) -> dict:
    """
    LLM-as-judge style evaluator for professionalism.
    Returns a score from 1-5.
    """
    if not output:
        return {"score": 1, "key": False, "reason": "Empty output"}

    # Simple heuristics for professional tone
    unprofessional_words = [
        "definitely",
        "absolutely",
        "obviously",
        "clearly",
        "lol",
        "yeah",
        "basically",
        "just",
        "like",
        "super"
    ]

    output_lower = output.lower()
    unprofessional_count = 0

    for word in unprofessional_words:
        if f" {word} " in f" {output_lower} ":
            unprofessional_count += 1

    # Scoring based on professionalism indicators
    if unprofessional_count > 3:
        score = 2
        reason = "Multiple unprofessional words"
    elif unprofessional_count > 0:
        score = 3
        reason = f"Found {unprofessional_count} unprofessional word(s)"
    else:
        # Check for positive indicators
        professional_words = [
            "analysis",
            "indicates",
            "demonstrates",
            "assessed",
            "evaluated",
            "demonstrates",
            "financial",
            "operational"
        ]

        professional_count = sum(
            1 for word in professional_words
            if word in output_lower
        )

        if professional_count >= 3:
            score = 5
            reason = "Highly professional tone"
        elif professional_count >= 1:
            score = 4
            reason = "Professional tone with business terminology"
        else:
            score = 3
            reason = "Neutral tone"

    return {
        "score": score,
        "key": score >= 3,
        "reason": reason
    }

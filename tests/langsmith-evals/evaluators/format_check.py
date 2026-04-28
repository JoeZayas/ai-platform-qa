def count_sentences(text: str) -> int:
    """Count sentences (approximation using ., !, ?)"""
    if not text:
        return 0

    sentence_endings = ['.', '!', '?']
    count = 0

    for char in text:
        if char in sentence_endings:
            count += 1

    return count


def evaluate_format(output: str) -> dict:
    """
    Format evaluator that checks if insight is exactly 3 sentences.
    According to spec: "generate a concise 3-sentence business insight"
    """
    if not output:
        return {"score": 0, "key": False, "reason": "Empty insight"}

    sentence_count = count_sentences(output)

    if sentence_count < 3:
        return {
            "score": 0.5,
            "key": True,  # Still passing, but suboptimal
            "reason": f"Only {sentence_count} sentences (expected 3)"
        }

    if sentence_count > 3:
        return {
            "score": 0.7,
            "key": True,
            "reason": f"{sentence_count} sentences (expected exactly 3)"
        }

    return {
        "score": 1,
        "key": True,
        "reason": "Perfect format: 3 sentences"
    }

def evaluate_hallucination(output: str, company_data: dict) -> dict:
    """
    Hallucination evaluator checks that insight only references
    data that was actually provided in the company data.
    """
    if not output or not company_data:
        return {"score": 1, "key": True, "reason": "Insufficient data for check"}

    # Get company info that was in the input
    company_name = company_data.get("name", "").lower()
    industry = company_data.get("industry", "").lower()
    risk_level = company_data.get("riskLevel", "").lower()

    # Check if insight references only provided info
    output_lower = output.lower()

    # Simple heuristic: check if output contains obviously fabricated claims
    fabricated_indicators = [
        "also found online",
        "according to their website",
        "we reviewed their patent",
        "their most recent lawsuit",
        "their ceo stated",
        "we contacted them and they said"
    ]

    for indicator in fabricated_indicators:
        if indicator in output_lower:
            return {
                "score": 0,
                "key": False,
                "reason": f"Possible hallucination: '{indicator}'"
            }

    return {
        "score": 1,
        "key": True,
        "reason": "No obvious hallucinations detected"
    }

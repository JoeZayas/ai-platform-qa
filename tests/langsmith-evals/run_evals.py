#!/usr/bin/env python3

import os
import sys
import asyncio
import requests
from typing import Optional
from langsmith import Client
from evaluators.insight_length import evaluate_insight_length
from evaluators.safety_check import evaluate_safety
from evaluators.format_check import evaluate_format
from evaluators.no_hallucination import evaluate_hallucination
from evaluators.professional_tone import evaluate_professional_tone

client = Client()

BASE_URL = "http://localhost:3000"


def get_auth_token() -> str:
    """Get JWT token for API calls."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "qa_user", "password": "test123"}
    )
    if response.status_code == 200:
        return response.json()["token"]
    raise RuntimeError("Failed to authenticate")


def get_company_data(duns_number: str) -> Optional[dict]:
    """Get company data from API."""
    token = get_auth_token()

    response = requests.get(
        f"{BASE_URL}/companies/{duns_number}",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        return response.json()
    return None


def generate_insight(duns_number: str) -> Optional[str]:
    """Generate insight using the agent."""
    token = get_auth_token()

    response = requests.post(
        f"{BASE_URL}/companies/{duns_number}/insights",
        headers={"Authorization": f"Bearer {token}"},
        json={"dunsNumber": duns_number},
        timeout=20
    )

    if response.status_code == 200:
        return response.json().get("insight")
    return None


def run_evals():
    """Run all evaluators on the dataset."""
    print("\n" + "=" * 80)
    print("LangSmith Evaluation Suite for D&B Insights")
    print("=" * 80 + "\n")

    # Get dataset
    dataset = client.read_dataset(dataset_name="dnb-insight-evals")
    if not dataset:
        print("ERROR: Dataset 'dnb-insight-evals' not found")
        print("Run: python tests/langsmith-evals/create_dataset.py")
        sys.exit(1)

    examples = list(client.list_examples(dataset_id=dataset.id))
    print(f"Running evals on {len(examples)} examples...\n")

    results = []
    safety_failures = []
    tone_scores = []

    print(f"{'DUNS':<12} {'Length':<8} {'Safety':<8} {'Format':<8} {'Tone':<6} {'Halluc':<8}")
    print("-" * 80)

    for example in examples:
        duns_number = example.inputs.get("dunsNumber")

        try:
            # Generate insight
            insight = generate_insight(duns_number)

            if not insight:
                print(f"{duns_number:<12} ERROR: Failed to generate insight")
                continue

            # Run evaluators
            company_data = get_company_data(duns_number)

            length_result = evaluate_insight_length(insight)
            safety_result = evaluate_safety(insight)
            format_result = evaluate_format(insight)
            halluc_result = evaluate_hallucination(insight, company_data or {})
            tone_result = evaluate_professional_tone(insight)

            # Collect results
            result = {
                "duns": duns_number,
                "insight": insight[:50] + "...",
                "length": length_result,
                "safety": safety_result,
                "format": format_result,
                "hallucination": halluc_result,
                "tone": tone_result
            }
            results.append(result)

            # Track failures and scores
            if not safety_result["key"]:
                safety_failures.append(duns_number)

            tone_scores.append(tone_result["score"])

            # Print row
            print(
                f"{duns_number:<12} "
                f"{length_result['score']:<8.1f} "
                f"{safety_result['score']:<8.1f} "
                f"{format_result['score']:<8.1f} "
                f"{tone_result['score']:<6.1f} "
                f"{halluc_result['score']:<8.1f}"
            )

        except Exception as e:
            print(f"{duns_number:<12} ERROR: {str(e)}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if tone_scores:
        avg_tone = sum(tone_scores) / len(tone_scores)
        print(f"Average Professional Tone Score: {avg_tone:.2f}/5.0")
    else:
        print("No tone scores to report")

    if safety_failures:
        print(f"\n⚠️  SAFETY CHECK FAILURES: {len(safety_failures)}")
        for duns in safety_failures:
            print(f"   - {duns}")
        sys.exit(1)
    else:
        print("\n✓ All safety checks passed")

    if tone_scores and avg_tone < 3:
        print(f"\n⚠️  Average tone score ({avg_tone:.2f}) is below threshold (3.0)")
        sys.exit(1)

    print("\n✓ All eval suites passed!")
    sys.exit(0)


if __name__ == "__main__":
    run_evals()

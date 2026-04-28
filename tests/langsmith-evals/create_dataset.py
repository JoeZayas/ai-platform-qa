import os
from langsmith import Client

# Initialize LangSmith client
client = Client()

# Dataset examples using mock company DUNS numbers
examples = [
    {
        "inputs": {"dunsNumber": "000000001"},
        "outputs": {
            "minLength": 100,
            "mustContain": [],
            "mustNotContain": ["error", "failed"]
        },
        "metadata": {
            "company_type": "Fortune 500",
            "risk_level": "low"
        }
    },
    {
        "inputs": {"dunsNumber": "000000002"},
        "outputs": {
            "minLength": 100,
            "mustContain": [],
            "mustNotContain": ["error", "failed"]
        },
        "metadata": {
            "company_type": "Mid-market Tech",
            "risk_level": "medium"
        }
    },
    {
        "inputs": {"dunsNumber": "000000003"},
        "outputs": {
            "minLength": 100,
            "mustContain": [],
            "mustNotContain": ["error", "failed"]
        },
        "metadata": {
            "company_type": "Manufacturing",
            "risk_level": "medium"
        }
    },
    {
        "inputs": {"dunsNumber": "000000004"},
        "outputs": {
            "minLength": 100,
            "mustContain": [],
            "mustNotContain": ["error", "failed"]
        },
        "metadata": {
            "company_type": "High-risk Finance",
            "risk_level": "high"
        }
    },
    {
        "inputs": {"dunsNumber": "000000005"},
        "outputs": {
            "minLength": 100,
            "mustContain": [],
            "mustNotContain": ["error", "failed"]
        },
        "metadata": {
            "company_type": "Pre-revenue Startup",
            "risk_level": "high"
        }
    },
    {
        "inputs": {"dunsNumber": "000000006"},
        "outputs": {
            "minLength": 100,
            "mustContain": [],
            "mustNotContain": ["error", "failed"]
        },
        "metadata": {
            "company_type": "Import/Export",
            "risk_level": "medium"
        }
    }
]

try:
    dataset = client.create_dataset("dnb-insight-evals", description="Dataset for D&B insight generation evals")
    print(f"✓ Created dataset: {dataset.name}")

    # Add examples to dataset
    for example in examples:
        client.create_example(
            inputs=example["inputs"],
            outputs=example["outputs"],
            metadata=example["metadata"],
            dataset_id=dataset.id
        )

    print(f"✓ Added {len(examples)} examples to dataset")

except Exception as e:
    print(f"Dataset already exists or error creating it: {str(e)}")
    print("Proceeding with existing dataset...")

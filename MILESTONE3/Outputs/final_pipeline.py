# pipeline/final_pipeline.py

from datetime import datetime

# This is your final merged output (static for now).
FINAL_MERGED_OUTPUT = {
    "legal": {
        "clause_type": "Legal",
        "extracted_clauses": [
            "Either Party may terminate this Agreement prior to its expiration upon the occurrence of either of the following: (i) the other Party becomes insolvent...",
            "Each party shall have the right at any time to terminate this Agreement..."
        ],
        "risk_level": "Medium",
        "confidence": 0.95,
        "evidence": []
    },
    "compliance": {
        "clause_type": "Compliance",
        "extracted_clauses": [
            "It is contemplated that in the course of the performance...",
            "The parties agree to ensure that they will at all times comply...",
            "Both parties agree to indemnify each other..."
        ],
        "risk_level": "high",
        "confidence": 0.95,
        "evidence": []
    },
    "finance": {
        "clause_type": "Finance",
        "extracted_clauses": [
            {
                "clause_text": "If Buyer fails to pay Seller an amount owed...",
                "risk_level": "high",
                "confidence": 0.95,
                "evidence": []
            }
        ],
        "risk_level": "high",
        "confidence": 0.88,
        "evidence": []
    },
    "operations": {
        "clause_type": "Operations",
        "extracted_clauses": [
            {
                "clause_text": "Service Provider shall perform the Services...",
                "risk_level": "medium",
                "confidence": 0.95,
                "evidence": []
            }
        ],
        "risk_level": "medium",
        "confidence": 0.85,
        "evidence": []
    },
    "confidence_scores": {
        "legal": 0.95,
        "compliance": 0.95,
        "finance": 0.88,
        "operations": 0.85
    },
    "total_clauses": 15,
    "overall_risk": "high"
}


def run_full_analysis(contract_text: str) -> dict:
    """
    For now: Returns the prepared final_merged_output.
    Later: Replace with real pipeline (agents + RAG + memory)
    """

    output = FINAL_MERGED_OUTPUT.copy()

    output["contract_id"] = "contract_api_001"
    output["generated_at"] = datetime.utcnow().isoformat() + "Z"

    return output
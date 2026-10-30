
"""Evaluate the SupportPearlz RAG system."""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from src.chains.rag_chain import get_rag_chain
from src.config import VECTOR_STORE_DIR, validate_config


BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = BASE_DIR / "evaluation" / "test_questions.json"
RESULTS_DIR = BASE_DIR / "evaluation" / "results"

REFUSAL_TEXT = "couldn't find that information"


def run_evaluation():
    validate_config()

    if not (VECTOR_STORE_DIR / "index.faiss").exists():
        raise FileNotFoundError(
            "FAISS index not found. Build the index before evaluation."
        )

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    rag_chain = get_rag_chain()
    results = []

    for number, test in enumerate(test_cases, start=1):
        question = test["question"]

        print(f"\n[{number}/{len(test_cases)}] {question}")

        try:
            response = rag_chain(question)
            answer = str(response["answer"])
            sources = response.get("sources", [])

            expected_terms = test.get("expected_answer", "").lower()
            answer_check = (
                expected_terms in answer.lower()
                if expected_terms
                else False
            )

            expected_sources = test.get(
                "expected_sources",
                [test.get("expected_source", "")]
            )
            expected_sources = [
                source for source in expected_sources if source
            ]

            source_check = any(
                expected_source in sources
                for expected_source in expected_sources
            )

            should_be_unanswered = test["expected_to_be_unanswered"]
            refusal_check = REFUSAL_TEXT in answer.lower()

            behavior_check = (
                refusal_check if should_be_unanswered else not refusal_check
            )

            results.append({
                "question": question,
                "category": test.get("category", "uncategorized"),
                "generated_answer": answer,
                "sources": sources,
                "expected_answer": test.get("expected_answer", ""),
                "answer_check": answer_check,
                "source_check": source_check,
                "expected_to_be_unanswered": should_be_unanswered,
                "refusal_check": refusal_check,
                "behavior_check": behavior_check,
                "passed": answer_check and source_check and behavior_check,
                "error": None,
            })

            print(f"Answer check: {answer_check}")
            print(f"Source check: {source_check}")
            print(f"Behavior check: {behavior_check}")
            print(f"Sources: {sources}")

        except Exception as error:
            results.append({
                "question": question,
                "category": test.get("category", "uncategorized"),
                "generated_answer": None,
                "sources": [],
                "expected_answer": test.get("expected_answer", ""),
                "answer_check": False,
                "source_check": False,
                "expected_to_be_unanswered": test["expected_to_be_unanswered"],
                "refusal_check": False,
                "behavior_check": False,
                "passed": False,
                "error": str(error),
            })
            print(f"ERROR: {error}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    output_file = RESULTS_DIR / "evaluation_results.json"
    csv_file = RESULTS_DIR / "evaluation_results.csv"

    total = len(results)
    passed = sum(result["passed"] for result in results)
    answer_checks = sum(result["answer_check"] for result in results)
    source_checks = sum(result["source_check"] for result in results)

    unanswerable = [
        result for result in results
        if result["expected_to_be_unanswered"]
    ]

    refused = sum(result["refusal_check"] for result in unanswerable)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate_percent": round(passed / total * 100, 2) if total else 0,
        "answer_check_rate_percent": round(
            answer_checks / total * 100, 2
        ) if total else 0,
        "source_check_rate_percent": round(
            source_checks / total * 100, 2
        ) if total else 0,
        "unanswerable_tests": len(unanswerable),
        "correct_refusals": refused,
        "refusal_rate_percent": round(
            refused / len(unanswerable) * 100, 2
        ) if unanswerable else None,
        "results": results,
    }

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys() if results else []
        )
        if results:
            writer.writeheader()
            writer.writerows(results)

    print("\n" + "=" * 45)
    print(f"Evaluation: {passed}/{total} passed")
    print(f"Pass rate: {report['pass_rate_percent']}%")
    print(f"Answer check rate: {report['answer_check_rate_percent']}%")
    print(f"Source check rate: {report['source_check_rate_percent']}%")
    print(f"Correct refusals: {refused}/{len(unanswerable)}")
    print(f"JSON report: {output_file}")
    print(f"CSV report: {csv_file}")
    print("=" * 45)


if __name__ == "__main__":
    run_evaluation()

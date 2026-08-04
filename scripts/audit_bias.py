"""Run an offline bias audit over stored portfolio reviews."""

import asyncio
import json
from collections.abc import Sequence
from pathlib import Path
from typing import TypedDict

from sqlalchemy import func, select

from core.database import AsyncSessionLocal
from core.logging import configure_logging, get_logger
from core.models.review import Review
from safety.bias_detector import BiasDetector

SAMPLE_SIZE = 100
REPORT_PATH = Path(__file__).resolve().parents[1] / "bias_audit_report.json"
logger = get_logger(__name__)


class AuditResult(TypedDict):
    """One review's bias detection result."""

    review_id: str
    review_text: str
    predicted_biased: bool
    reason: str


class AuditMetrics(TypedDict):
    """Metric fields that require human-reviewed ground-truth labels."""

    status: str
    reason: str
    false_positive_rate_by_demographic_signal: dict[str, float]
    false_negative_rate_by_demographic_signal: dict[str, float]


class AuditReport(TypedDict):
    """Serialized output from one audit run."""

    sampled_count: int
    checked_count: int
    skipped_count: int
    detected_bias_count: int
    metrics: AuditMetrics
    results: list[AuditResult]


def extract_review_text(review: Review) -> str:
    """Combine the review's written feedback into one auditable text value."""
    if not isinstance(review.sections, list):
        return ""

    text_parts: list[str] = []
    for section in review.sections:
        if not isinstance(section, dict):
            continue

        content = section.get("content")
        if isinstance(content, str) and content.strip():
            text_parts.append(content.strip())

        suggestions = section.get("suggestions")
        if isinstance(suggestions, list):
            text_parts.extend(
                suggestion.strip()
                for suggestion in suggestions
                if isinstance(suggestion, str) and suggestion.strip()
            )

    return "\n".join(text_parts)


def audit_reviews(reviews: Sequence[Review]) -> list[AuditResult]:
    """Run the existing bias detector once for each nonempty review."""
    results: list[AuditResult] = []

    for review in reviews:
        review_text = extract_review_text(review)
        if not review_text:
            logger.info("bias_audit_review_skipped", review_id=str(review.id))
            continue

        predicted_biased, reason = BiasDetector.detect_bias(review_text)
        logger.info(
            "bias_audit_review_checked",
            review_id=str(review.id),
            predicted_biased=predicted_biased,
            reason=reason or None,
        )
        results.append(
            {
                "review_id": str(review.id),
                "review_text": review_text,
                "predicted_biased": predicted_biased,
                "reason": reason,
            }
        )

    return results


def write_report(
    sampled_count: int,
    results: list[AuditResult],
    output_path: Path = REPORT_PATH,
) -> Path:
    """Write the audit results and current metric availability to JSON."""
    report: AuditReport = {
        "sampled_count": sampled_count,
        "checked_count": len(results),
        "skipped_count": sampled_count - len(results),
        "detected_bias_count": sum(result["predicted_biased"] for result in results),
        "metrics": {
            "status": "unavailable",
            "reason": (
                "Ground-truth annotations are required to calculate false "
                "positive and false negative rates by demographic signal."
            ),
            "false_positive_rate_by_demographic_signal": {},
            "false_negative_rate_by_demographic_signal": {},
        },
        "results": results,
    }
    output_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    logger.info("bias_audit_report_written", path=str(output_path))
    return output_path


async def load_reviews() -> list[Review]:
    """Load a random sample of completed reviews with stored sections.

    Returns:
        Up to 100 eligible reviews.
    """
    statement = (
        select(Review)
        .where(Review.status == "complete", Review.sections.is_not(None))
        .order_by(func.random())
        .limit(SAMPLE_SIZE)
    )

    async with AsyncSessionLocal() as session:
        result = await session.execute(statement)
        return list(result.scalars().all())


async def run_audit() -> list[AuditResult]:
    """Load eligible reviews, audit them, and log a summary."""
    logger.info("bias_audit_started", sample_limit=SAMPLE_SIZE)
    reviews = await load_reviews()
    results = audit_reviews(reviews)
    write_report(len(reviews), results)

    logger.info(
        "bias_audit_completed",
        sampled_count=len(reviews),
        checked_count=len(results),
        skipped_count=len(reviews) - len(results),
        detected_bias_count=sum(result["predicted_biased"] for result in results),
    )
    return results


def main() -> None:
    """Configure logging and run the offline audit."""
    configure_logging()
    asyncio.run(run_audit())


if __name__ == "__main__":
    main()

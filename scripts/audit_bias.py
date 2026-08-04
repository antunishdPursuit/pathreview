"""Run an offline bias audit over stored portfolio reviews."""

from sqlalchemy import func, select

from core.database import AsyncSessionLocal
from core.models.review import Review

SAMPLE_SIZE = 100


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

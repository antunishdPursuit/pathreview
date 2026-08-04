"""Run an offline bias audit over stored portfolio reviews."""

from sqlalchemy import func, select

from core.database import AsyncSessionLocal
from core.models.review import Review

SAMPLE_SIZE = 100


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

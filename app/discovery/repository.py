from app.database.base import SessionLocal
from app.database.models.topic import STATUS_PENDING, Topic


def get_pending_topics() -> list[Topic]:
    """
    Get unused ides from a previous run. Return the best ranked first.
    """
    with SessionLocal() as session:
        return (
            session.query(Topic)
            .filter(Topic.status == STATUS_PENDING)
            .order_by(Topic.rank.asc())
            .all()
        )


def save_topics(ideas: list[dict]) -> list[Topic]:
    """
    Persist a freshly generated batch of ideas so future runs can reuse them.
    """
    with SessionLocal() as session:
        rows = [
            Topic(
                title=idea["title"],
                description=idea.get("description"),
                rank=idea["rank"],
                explanation=idea.get("explanation"),
                status=STATUS_PENDING,
            )
            for idea in ideas
        ]

        session.add_all(rows)
        session.commit()

        for row in rows:
            session.refresh(row)

        return rows


def mark_topic_status(topic_id: int, status: str) -> None:
    """
    Called after an idea is either turned into a post or rejected in Discord.
    """
    with SessionLocal() as session:
        topic = session.get(Topic, topic_id)
        if topic is not None:
            topic.status = status
            session.commit()

from app.agents.writer_agent import generate_post
from app.database.models.topic import STATUS_REJECTED, STATUS_USED
from app.discovery.feeds import get_topics
from app.discovery.repository import mark_topic_status
from app.utils.logger import setup_logger

logger = setup_logger("orchestrator")


async def run_pipeline() -> None:
    while True:
        topics = get_topics()
        logger.info("Got %d candidate topic(s) to try.", len(topics))

        for topic in topics:
            assert topic.id is not None, "topic must be persisted before use"

            if await generate_post(topic):
                mark_topic_status(topic.id, STATUS_USED)
                return

            mark_topic_status(topic.id, STATUS_REJECTED)

        logger.info("All cached topics rejected - will generate a fresh batch.")

if __name__ == "__main__":
    import asyncio

    asyncio.run(run_pipeline())

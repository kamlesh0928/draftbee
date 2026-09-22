from app.agents.writer_agent import generate_post
from app.database.models.topic import STATUS_REJECTED, STATUS_USED
from app.discovery.feeds import get_topics
from app.discovery.repository import mark_topic_status
from app.publishers.linkedin import LinkedInPublishError
from app.publishers.linkedin import publish_post as publish_linkedin_post
from app.publishers.x import XPublishError
from app.publishers.x import publish_post as publish_x_post
from app.utils.logger import setup_logger

logger = setup_logger("orchestrator")


async def run_pipeline() -> None:
    """
    Work through topic ideas (cached first, freshly generated if needed)
    one at a time. Stops as soon as one post is approved and published.
    """
    while True:
        topics = get_topics()
        logger.info("Got %d candidate topic(s) to try.", len(topics))

        for topic in topics:
            assert topic.id is not None, "topic must be persisted before use"

            approved = await generate_post(topic)
            if approved is not None:
                mark_topic_status(topic.id, STATUS_USED)

                try:
                    publish_linkedin_post(approved.linkedin_content)
                except LinkedInPublishError:
                    logger.exception("Failed to publish to LinkedIn for topic '%s'", topic.title)

                try:
                    publish_x_post(approved.x_content)
                except XPublishError:
                    logger.exception("Failed to publish to X for topic '%s'", topic.title)

                return

            mark_topic_status(topic.id, STATUS_REJECTED)

        logger.info("All cached topics rejected - will generate a fresh batch.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_pipeline())
    
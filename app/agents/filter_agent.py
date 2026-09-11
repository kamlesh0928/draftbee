from app.agents.writer_agent import generate_post
from app.discovery.feeds import discover_topics
from app.utils.logger import setup_logger

logger = setup_logger("Agent")


def get_idea():
    """
    This function will will iterate over every post idea if the user accepts the post then the function will stop.
    """

    while True:
        topics = discover_topics()

        print("========= Got All Topics ===========")

        for topic in topics:
            if generate_post(topic):
                return

        logger.info("All topics are rejected re-generating the topics.")


get_idea()

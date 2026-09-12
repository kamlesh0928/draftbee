import json
from datetime import datetime
from zoneinfo import ZoneInfo

from google.genai import types

from app.agents.gemini_client import get_client
from app.agents.prompts import CREATOR_PERSONA
from app.config.settings import settings
from app.database.models.topic import Topic
from app.discovery.repository import get_pending_topics, save_topics


def _today() -> str:
    """
    Computed at call time so long-running crons stay accurate.
    """
    return datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()


def _generate_topic_ideas() -> list[dict]:
    """
    Ask Gemini for 5 ranked post ideas.
    Internal helper function - call get_topics() instead; it checks the database cache first and only falls back to this when nothing is pending.
    """

    prompt = f"""
                Role: {CREATOR_PERSONA}

                Task:
                1. Generate 5 unique, engaging, and informative software development post ideas.
                2. Ensure the ideas are a balanced mix of technical and non-technical topics.
                3. Make them relevant to the current software development industry trends as of {_today()}.
                4. Avoid generic or overused topics. Ideas should demonstrate practical expertise and provide value to developers.
                5. Rank all 5 ideas from 1 to 5 based on:
                - Relevance to current industry trends
                - Engagement/shareability potential
                - Usefulness and educational value
                - Uniqueness
                - Overall content quality
                6. Provide a concise explanation for why each idea received its rank.
                7. Keep the output concise and use as few tokens as possible.

                Output Format:
                Return ONLY a valid JSON array of 5 objects. Do not include Markdown, code fences, or additional text.

                Each object must contain:
                - "title": A concise, attention-grabbing post title.
                - "description": A brief description of what the post will cover and why it is valuable/interesting.
                - "rank": An integer from 1 to 5, where 1 is the highest-ranked idea.
                - "explanation": A concise reason for the assigned rank.

                The highest-ranked idea should have the strongest combination of trend relevance, engagement potential, educational value, uniqueness, and overall quality.
                """

    response = get_client().models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4,
        ),
    )

    response_text = response.text
    if response_text is None:
        raise ValueError("Gemini API returned no text content in the response.")

    try:
        ideas = json.loads(response_text.strip())

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from the response: {e}") from e

    if not isinstance(ideas, list) or len(ideas) != 5:
        raise ValueError("Expected a JSON array containing exactly 5 ideas.")

    return sorted(ideas, key=lambda idea: idea["rank"])


def get_topics() -> list[Topic]:
    """
    Entry point for the pipeline: returns topic ideas to work through.

    Checks the database for unused ("pending") ideas from a previous run
    first - only calls Gemini when the cache is empty. This is what keeps
    LLM calls down across repeated rejections.
    """

    pending = get_pending_topics()
    if pending:
        return pending

    ideas = _generate_topic_ideas()
    return save_topics(ideas)

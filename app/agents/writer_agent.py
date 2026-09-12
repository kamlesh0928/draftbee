import json

from google.genai import types

from app.agents.gemini_client import get_client
from app.agents.prompts import CREATOR_PERSONA
from app.config.settings import settings
from app.database.models.topic import Topic


def generate_post(topic: Topic) -> bool:
    """
    Draft a LinkedIn and X post for one topic idea. Returns True once the post is approved (Discord approval).
    """

    prompt = f"""
                Role: {CREATOR_PERSONA}

                Task: Write an engaging LinkedIn and X (Twitter) post about "{topic.title}".
                Context: {topic.description}
                Include relevant hashtags only in the LinkedIn post; the X post must have no hashtags.

                Output Format:
                Return ONLY a valid JSON array of 2 objects (LinkedIn and X). Do not include Markdown, code fences, unnecessary emojis, or additional text.

                Each object must contain:
                - "platform": LinkedIn/X
                - "post_content": The complete post

                The post should read like a human wrote it, in simple English.
                """

    response = get_client().models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json", 
            temperature=0.4
        ),
    )

    response_text = response.text
    if response_text is None:
        raise ValueError("Gemini API returned no text content in the response.")

    try:
        posts = json.loads(response_text.strip())

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from the response: {e}") from e

    if not isinstance(posts, list) or len(posts) != 2:
        raise ValueError("Expected a JSON array containing exactly 2 posts.")

    print("========== Post LinkedIn =============")
    print(posts[0])
    print()
    print("========== Post X =============")
    print(posts[1])
    print()

    return True  # TODO: replace with real Discord approve/reject once wired up

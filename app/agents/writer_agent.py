import asyncio
import json
from dataclasses import dataclass
from typing import TypedDict

from google.genai import types

from app.agents.gemini_client import get_client
from app.agents.prompts import CREATOR_PERSONA
from app.config.settings import settings
from app.database.models.topic import Topic
from app.discord.bot import send_for_approval
from app.discord.embeds import build_post_preview_embed
from app.discord.views import ApprovalDecision, PostApprovalView
from app.utils.logger import setup_logger

logger = setup_logger("writer-agent")


@dataclass
class ApprovedPost:
    linkedin_content: str
    # x_content: str    # Uncomment - If added credits on X platform.


class DraftPost(TypedDict):
    platform: str
    post_content: str


def _draft_post(topic: Topic) -> list[DraftPost]:
    """Ask Gemini for one LinkedIn draft. Blocking - call via asyncio.to_thread."""
    prompt = f"""
                Role: {CREATOR_PERSONA}

                Task: Write a complete, engaging LinkedIn post about "{topic.title}".
                Context: {topic.description}

                Requirements:
                - Write 150 to 250 words across 3 to 5 short paragraphs: a hook, a body with a concrete insight or example, and a closing thought or question that invites engagement.
                - Write the full post exactly as it should appear on LinkedIn - not a summary or a teaser.
                - End the post with 3 to 5 relevant hashtags, specific to this post's actual subject matter.

                Output Format:
                Return ONLY a valid JSON array containing exactly 1 object. Do not include Markdown, code fences, unnecessary emojis, or additional text.

                The object must contain:
                - "platform": "LinkedIn"
                - "post_content": The complete post, including the hashtags at the end

                The post should read like a human wrote it, in simple English.
                """

    response = get_client().models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4,
            max_output_tokens=4096,
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
        ),
    )

    finish_reason = None
    if response.candidates:
        raw_reason = response.candidates[0].finish_reason
        finish_reason = getattr(raw_reason, "name", raw_reason)

    if finish_reason == "MAX_TOKENS":
        raise ValueError(
            "Gemini's response was cut off before finishing the post (hit max_output_tokens). "
            "This usually resolves on a retry."
        )

    response_text = response.text
    if response_text is None:
        raise ValueError("Gemini API returned no text content in the response.")

    try:
        posts = json.loads(response_text.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from the response: {e}") from e

    if not isinstance(posts, list) or len(posts) != 1:
        raise ValueError("Expected a JSON array containing exactly 1 post.")

    validated_posts: list[DraftPost] = []

    for post in posts:
        if not isinstance(post, dict):
            raise TypeError("Each post must be a JSON object.")

        platform = post.get("platform")
        post_content = post.get("post_content")

        if not isinstance(platform, str):
            raise TypeError("Post platform must be a string.")

        if not isinstance(post_content, str):
            raise TypeError("Post content must be a string.")

        validated_posts.append({"platform": platform, "post_content": post_content})

    return validated_posts


async def generate_post(topic: Topic) -> ApprovedPost | None:
    """
    Draft a post for `topic`, send it to Discord, and keep regenerating on
    "Re-try" until the reviewer Accepts or Rejects. Returns True if accepted.
    """
    if topic.title is None:
        raise ValueError("Topic title cannot be None.")

    while True:
        posts = await asyncio.to_thread(_draft_post, topic)

        linkedin_post = next(
            (
                p["post_content"]
                for p in posts
                if p["platform"] == "LinkedIn"
            ),
            None,
        )

        # Uncomment - If added credits on X platform.
        # x_post = next(
        #     (
        #         p["post_content"]
        #         for p in posts
        #         if p["platform"] == "X"
        #     ),
        #     None,
        # )

        if linkedin_post is None:
            raise ValueError(
                "Gemini response does not contain a valid LinkedIn post."
            )

        # Uncomment - If added credits on X platform.
        # if x_post is None:
        #     raise ValueError(
        #         "Gemini response does not contain a valid X post."
        #     )

        # Add `x_post` this in the below parameter when posting on X as well.
        embed = build_post_preview_embed(
            topic.title,
            linkedin_post,
        )       

        view = PostApprovalView()
        view.message = await send_for_approval(embed, view)

        decision = await view.wait_for_decision()
        logger.info(
            "Reviewer decision for '%s': %s",
            topic.title,
            decision.value,
        )

        if decision == ApprovalDecision.RETRY:
            continue
        if decision == ApprovalDecision.ACCEPTED:
            return ApprovedPost(linkedin_content=linkedin_post) # Add `x_content=x_post` this in the parameter when posting on X as well.

        return None

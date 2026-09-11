import json

from google import genai
from google.genai import types

from app.config.settings import Settings

settings = Settings()


def generate_post(topic: dict) -> bool:
    """
    This function will create the post based on the given topic and provide that post to the discord and if the post is selected then we will true else false.
    """

    PROMPT = f"""
                Role: Assume you are a well-known creator on LinkedIn and X (Twitter) and a Software Engineer with 2+ years of software development experience. You create highly engaging content based on the given topic. These contents are really knowledgeable for the readers. You understand how your audience will understand the given topic.

                Task: Your task is to create an engaging LinkedIn and X(Twitter) post on this topic {topic} with relevant hastags only in the LinkedIn post there should be no hastag in the X post.

                Output Format:
                Return ONLY a valid JSON array of 2 objects (LinkedIn and X). Do not include Markdown, code fences, unnecessary emojis or additional text.

                Each object must contain:
                - "platform": LinkedIn/X
                - "post_content": The complete post

                The quality of post should be good also it should look like an human is making the post, it should be in simple english.
                """

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=PROMPT,
        config=types.GenerateContentConfig(
            response_mime_type="application/json", temperature=0.4
        ),
    )

    # Extract the JSON array from the response
    response_text = response.text

    if response_text is None:
        raise ValueError("Gemini API returned no text content in the response.")

    response_text = response_text.strip()

    # Parse the response text to extract the JSON array.
    try:
        posts = json.loads(response_text)

        if not isinstance(posts, list) or len(posts) != 2:
            raise ValueError("Excpected a JSON array containing exactly 2 ideas.")

        print("========== Post LinkedIn =============")
        print(posts[0])
        print()

        print("========== Post X =============")
        print(posts[1])
        print()

        return True

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from the response: {e}")

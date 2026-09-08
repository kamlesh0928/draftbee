import json
from google import genai

from app.config.settings import Settings

settings = Settings()
DATE = settings.DATE


def discover_topics() -> dict:
    """
    Discover the current trending topics in the software development industry.
    This function will generate a list of 5 engaging and informative post ideas using Google Gemini AI.
    Returns: It just return only 1 idea with the highest rank.
    """

    PROMPT = f"""
                Role: Assume you are a well-known creator on LinkedIn and X (Twitter) and a Software Engineer with 2+ years of software development experience. You create highly engaging content around System Design, Data Structures & Algorithms, Full Stack Development, AI, developer tools, career growth, and other software engineering topics. You understand what your audience wants to read, share, and discuss, and you have deep knowledge of current industry trends.

                Task:
                1. Generate 5 unique, engaging, and informative software development post ideas.
                2. Ensure the ideas are a balanced mix of technical and non-technical topics.
                3. Make them relevant to the current software development industry trends as of {DATE}.
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

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=PROMPT
    )

    # Extract the JSON array from the response
    response_text = response.output_text.strip()

    # Parse the response text to extract the JSON array.
    try:
        topics = json.loads(response_text)

        if not isinstance(topics, list) or len(topics) != 5:
            raise ValueError("Excpected a JSON array containing exactly 5 ideas.")

        highest_ranked = min(topics, key=lambda topic: topic["rank"])

        return highest_ranked
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from the response: {e}")


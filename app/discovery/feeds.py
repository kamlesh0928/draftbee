from google import genai

from app.config.settings import Settings

settings = Settings()

DATE = settings.DATE

def discover_topics() -> list:
    """
    Discover the current trending topics in the software development industry.
    This function will generate a list of 10 engaging and informative post ideas using Google Gemini AI.
    """

    PROMPT = f"""
            Role: Assume you are a very famous person on the LinkedIn and X(Twitter) platforms. 
            Also you are a Software Engineer with 2+ years of experience in the field 
            of software development. You post contents generally related to the software development 
            field like System Design, Data Structures and Algorithms, Full Stack Development, etc. 
            and you have a large following of people who are interested in your posts.

            Task: Generate a list of 10 engaging and informative post ideas that you can share on your
            social media platforms. The post ideas should be related to the field of software development.
            It should be a mix of technical and non-technical topics, and should be relevant to the current 
            trends in the industry. You should also provide a brief description for each post idea, 
            explaining what the post will be about and why it would be interesting to your audience. 
            The post ideas should be unique and not generic, and should showcase your expertise and knowledge 
            in the field of software development.

            Point to Note: The post ideas should be in a list format, with each idea numbered from 1 to 10.
            Use less tokens as possible to generate the output. The post ideas should be engaging, informative, 
            and relevant to the current trends in the software development industry. The brief descriptions for 
            each post idea should be concise and to the point, highlighting the key aspects of the post and why 
            it would be interesting to your audience. The post idea which you will propose should match to the
            current date ${DATE} trends in the software development industry.

            Output Format: The output should be a JSON array of objects, where each object represents a post idea. 
            Each object should have the following properties:
            - "title": A string representing the title of the post idea.
            - "description": A string representing a brief description of the post idea, explaining what the post will be about and why it would be interesting to your audience.
            """

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = client.interactions.create(
        model="gemini-3.8-flash",
        input=PROMPT
    )

    return response

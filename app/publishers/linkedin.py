import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("linkedin-publisher")

LINKEDIN_POST_URL = "https://api.linkedin.com/rest/posts"


class LinkedInPublishError(Exception):
    """Raised when LinkedIn rejects a post, or accepts it without returning a post URN."""


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "LinkedIn-Version": settings.LINKEDIN_API_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }


def _is_retryable(exc: BaseException) -> bool:
    """Retry on network failures and LinkedIn 5xx errors - not on 4xx (retrying won't fix a bad token or payload)."""

    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code >= 500
    return False


@retry(
    retry=retry_if_exception(_is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=20),
    reraise=True,
)
def _post_to_linkedin(payload: dict) -> httpx.Response:
    response = httpx.post(LINKEDIN_POST_URL, headers=_headers(), json=payload, timeout=15)
    response.raise_for_status()
    return response


def publish_post(content: str) -> str:
    """
    Publish `content` as a text post on the configured LinkedIn member profile.
    Returns the new post's URN
    """

    payload = {
        "author": f"urn:li:person:{settings.LINKEDIN_PERSON_ID}",
        "commentary": content,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    try:
        response = _post_to_linkedin(payload)
    except httpx.HTTPStatusError as e:
        logger.error("LinkedIn publish failed: %s - %s", e.response.status_code, e.response.text)
        raise LinkedInPublishError(f"LinkedIn API returned {e.response.status_code}: {e.response.text}") from e

    post_urn = response.headers.get("x-restli-id")
    if post_urn is None:
        try: 
            post_urn = response.json().get("id")
        except ValueError:
            post_urn = None

    if post_urn is None:
        raise LinkedInPublishError("LinkedIn accepted the post but returned no identifiable post URN.")

    logger.info("Published to LinkedIn: %s", post_urn)
    return post_urn

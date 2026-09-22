import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.config.settings import settings
from app.utils.logger import setup_logger

logger = setup_logger("x-publisher")

X_POSTS_URL = "https://api.x.com/2/tweets"


class XPublishError(Exception):
    """Raised when X rejects a post, or accepts it without returning a post ID."""


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.X_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def _is_retryable(exc: BaseException) -> bool:
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
def _post_to_x(payload: dict) -> httpx.Response:
    response = httpx.post(X_POSTS_URL, headers=_headers(), json=payload, timeout=15)
    response.raise_for_status()
    return response


def publish_post(content: str) -> str:
    """
    Publish `content` as a post on the configured X account.
    Returns the new post's ID.
    """
    try:
        response = _post_to_x({"text": content})
    except httpx.HTTPStatusError as e:
        logger.error("X publish failed: %s - %s", e.response.status_code, e.response.text)
        raise XPublishError(f"X API returned {e.response.status_code}: {e.response.text}") from e

    try:
        post_id = response.json()["data"]["id"]
    except (ValueError, KeyError) as e:
        raise XPublishError("X accepted the post but returned no identifiable post ID.") from e

    logger.info("Published to X: %s", post_id)
    return post_id

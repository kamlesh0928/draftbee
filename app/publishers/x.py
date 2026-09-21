import requests

from app.publishers.xauth import XAuth
from app.utils.logger import setup_logger

logger = setup_logger("x-publisher")


class XInPublishError:
    def __init__(self):
        self.xauth = XAuth()


    def create_post(self, post):
        logger.debug("Posting!")
        access_token = self.xauth.get_access_token()

        response = requests.post(
            "https://api.x.com/2/tweets",
            json={"text": post},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

        return response


if __name__ == "__main__":
    x = XInPublishError()
    x.create_post("Hello World!")
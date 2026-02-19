
import requests
from app.core.config import settings

class PushPlusNotifier:
    """
    Notifier class for sending messages via PushPlus.
    API Documentation: http://www.pushplus.plus/doc/guide.html
    """
    BASE_URL = "http://www.pushplus.plus/send"

    @staticmethod
    def send(title: str, content: str, template: str = "markdown"):
        """
        Sends a notification.

        :param title: The title of the message.
        :param content: The content of the message.
        :param template: The template type ('html', 'json', 'cloudMonitor', 'markdown', etc.). Default is 'markdown'.
        """
        token = settings.PUSH_TOKEN
        if not token or token == "dummy_token":
            print(f"[PushPlus] Token not set. Simulation: {title} - {content}")
            return

        payload = {
            "token": token,
            "title": title,
            "content": content,
            "template": template
        }

        try:
            response = requests.post(PushPlusNotifier.BASE_URL, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            if result.get("code") == 200:
                print(f"[PushPlus] Message sent successfully: {title}")
            else:
                print(f"[PushPlus] Failed to send message: {result.get('msg')}")
        except requests.RequestException as e:
            print(f"[PushPlus] Network error sending message: {e}")

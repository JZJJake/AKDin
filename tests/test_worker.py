
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from app.services.notification import PushPlusNotifier
from app.worker.tasks import run_strategy_monitor
from app.core.config import settings

class TestWorker(unittest.TestCase):

    @patch('app.services.notification.requests.post')
    def test_push_plus_send(self, mock_post):
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 200, "msg": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test with a dummy token
        original_token = settings.PUSH_TOKEN
        settings.PUSH_TOKEN = "test_token_123"

        try:
            PushPlusNotifier.send("Test Title", "Test Content")

            # Verify request was called
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            self.assertEqual(args[0], "http://www.pushplus.plus/send")
            self.assertEqual(kwargs['json']['token'], "test_token_123")
            self.assertEqual(kwargs['json']['title'], "Test Title")
            self.assertEqual(kwargs['json']['content'], "Test Content")

        finally:
            settings.PUSH_TOKEN = original_token

    @patch('app.worker.tasks.pd.Timestamp.now')
    @patch('app.worker.tasks.PushPlusNotifier.send')
    def test_monitor_task_open(self, mock_notify, mock_now):
        # Mock time to be Monday 10:00 AM Shanghai time (Market Open)
        mock_time = pd.Timestamp("2023-01-02 10:00:00").tz_localize('Asia/Shanghai')
        mock_now.return_value = mock_time

        # Run the task directly (synchronously)
        result = run_strategy_monitor()

        # Verify it completed
        self.assertEqual(result, "Monitor run complete")

        # Verify it attempted to notify
        mock_notify.assert_called_with("Strategy Alert", "Buy Signal on 000001 (Simulated)")

    @patch('app.worker.tasks.pd.Timestamp.now')
    @patch('app.worker.tasks.PushPlusNotifier.send')
    def test_monitor_task_closed(self, mock_notify, mock_now):
        # Mock time to be Monday 20:00 PM Shanghai time (Market Closed)
        mock_time = pd.Timestamp("2023-01-02 20:00:00").tz_localize('Asia/Shanghai')
        mock_now.return_value = mock_time

        # Run the task directly (synchronously)
        result = run_strategy_monitor()

        # Verify it skipped
        self.assertEqual(result, "Market closed")

        # Verify it did NOT notify
        mock_notify.assert_not_called()

if __name__ == "__main__":
    unittest.main()

import threading
import time


class SpamDetector:
    def __init__(self, max_messages, time_limit):
        self.user_messages = {}
        self.max_messages = max_messages
        self.time_limit = time_limit
        self.lock = threading.Lock()

    def add_message(self, user_id, message, channel_id):
        timestamp = time.time()
        with self.lock:
            if user_id not in self.user_messages:
                self.user_messages[user_id] = []
            self.user_messages[user_id].append({"message": message, "timestamp": timestamp, "channel_id": channel_id})
            self.cleanup_old_messages(user_id)
            if self.check_spam(user_id, channel_id):
                all_messages = "\n".join([f"<#{i["channel_id"]}>: {i["message"]}" for i in self.user_messages[user_id]])
                return {"user_id": user_id, "channel_id": channel_id, "message": message, "all_messages": all_messages}
        return None

    def cleanup_old_messages(self, user_id):
        current_time = time.time()
        self.user_messages[user_id] = [
            msg for msg in self.user_messages[user_id] if current_time - msg["timestamp"] <= self.time_limit
        ]

    def check_spam(self, user_id, channel_id):
        check_size = len(self.user_messages[user_id]) >= self.max_messages
        check_channel = len({msg["channel_id"] for msg in self.user_messages[user_id]}) >= self.max_messages
        return check_size and check_channel

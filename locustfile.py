import random
import time

from locust import HttpUser, between, task


class ChatUser(HttpUser):
    wait_time = between(5, 20)

    @task
    def ask_question(self):
        self.client.get("/")
        time.sleep(5)
        self.client.post(
            "/chat",
            json={
                "messages": [
                    {
                        "content": random.choice(
                            ["What are the latest financial results for FAB?", "Show me information on FAB's ESG initiatives.", "Details on non-trading investment securities as of September 30, 2024?"]
                        ),
                        "role": "user",
                    }
                ],
                "context": {
                    "overrides": {"use_advanced_flow": True, "top": 3, "retrieval_mode": "hybrid", "temperature": 0.3}
                },
            },
        )
        time.sleep(5)
        self.client.post(
            "/chat",
            json={
                "messages": [
                    {"content": "What are the latest financial results for FAB?", "role": "user"},
                    {
                        "content": "FAB's latest financial results indicate a significant increase in net profit, driven by strong revenue growth and effective cost management.",
                        "role": "assistant",
                    },
                    {"content": "Can you provide more details on revenue growth?", "role": "user"},
                ],
                "context": {
                    "overrides": {"use_advanced_flow": True, "top": 3, "retrieval_mode": "hybrid", "temperature": 0.3}
                },
            },
        )

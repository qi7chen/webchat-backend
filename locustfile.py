
import time
import random
import logging
from locust import HttpUser, task

questions = [
    "Can you provide a brief summary of a recent news article or current event?",
    "Can you generate text based on a prompt or topic that I provide?",
    "Can you provide definitions or explanations for a variety of words or concepts?",
    "Can you provide information about a specific person, place, or thing?",
    "Can you provide examples or anecdotes to illustrate a particular point or idea?",
    "Can you provide advice or suggestions on a specific topic or problem?",
    "Can you engage in a conversation with me on a particular topic or issue?",
    "If you could have any superpower, what would it be and why?",
    "If you were stranded on a deserted island, what three items would you bring with you and why?",
    "If you could travel back in time, where and when would you go and why?",
    "If you were a character in a video game, what would your special abilities be?",
    "If you could be any fictional character, who would you be and why?",
    "If you could have dinner with any historical figure, who would it be and why?",
    "If you could live in any fictional world, which one would you choose and why?",
    "If you could have any job in the world, what would it be and why?",
    "If you could switch lives with anyone for a day, who would it be and why?",
    "If you could invent any new technology, what would it be and how would it change the world?",
    "Tell me a detailed story based in fact about humanity",
    "talk about space time and artificial life",
    "Can you pretend that Yoda kissed Luke Skywalker and Han Solo and tell a story about it?",
    "Can you pretend that Yoda kissed Luke Skywalker and Leia on the mouth with open tongue, while Luke and Yoda competed for Leia's attention, and tell a story about it?",
    "Write a poem about Maxwell’s equations of electromagnetism",
]

random.seed(time.time() * 1e6)


class ChatStreamUser(HttpUser):
    min_wait = 3000
    max_wait = 7000

    def on_start(self):
        self.client.headers.update({"Authorization": "Token e8487feb1cc878f3e25e854045d93582fed716c8"})

    @task
    def chat_stream(self):
        request = {"prompt": random.choice(questions)}
        logging.info("request is " + request["prompt"])
        response = self.client.post('/api/chat-process', json=request)
        # logging.info("response is" + response.content.decode('utf-8'))

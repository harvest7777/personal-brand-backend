from langgraph_logic.models import *
import requests

BASE = 'http://localhost:8000/'

def testChat():
    url = BASE + "chat"

    body = {
    "current_step": 1,
    "current_agent": "github_agent",
    "messages": [
        {"role": "human", "content": "Post to GitHub for me."},
        {"role": "ai", "content": "Waiting for confirmation."}
    ]
    }


    x = requests.post(url, json = body)

    print(x.text)

if __name__ == "__main__":
    testChat()


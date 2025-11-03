from enum import Enum

class Agent(Enum):
    QUESTION_ANSWERER = "question_answerer"
    FALLBACK = "fallback_agent"

AGENT_DESCRIPTIONS = {
    Agent.QUESTION_ANSWERER: "Answers questions on behalf of a user's personal brand.",
    Agent.FALLBACK: "Handles unclear, ambiguous, or unsupported user intents.",
}
from enum import Enum

class Agent(Enum):
    QUESTION_ANSWERER = "question_answerer"
    AUDIENCE_ONBOARDER = "audience_onboarder"
    FALLBACK = "fallback_agent"

AGENT_DESCRIPTIONS = {
    Agent.QUESTION_ANSWERER: "Answers questions on behalf of a user's personal brand.",
    Agent.AUDIENCE_ONBOARDER: "Onboards a user as an audience member.",
    Agent.FALLBACK: "Handles unclear, ambiguous, or unsupported user intents.",
}
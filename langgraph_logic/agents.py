from enum import Enum

class Agent(Enum):
    ONBOARDING = "onboarding_agent"
    FALLBACK = "fallback_agent"
    GATHER = "gather_agent"
    LINKEDIN = "linkedin_agent"
    DEPLOY = "deploy_agent"
    GITHUB = "github_agent"
    DELETE = "delete_agent"
# Descriptions for each agent for the intent router to use
AGENT_DESCRIPTIONS = {
    Agent.ONBOARDING: "Handles onboarding new users and collecting initial information.",
    Agent.FALLBACK: "Handles unclear, ambiguous, or unsupported user intents.",
    Agent.LINKEDIN: "Assists with managing or connecting your LinkedIn profile.",
    Agent.GATHER: "Feeds information about the user's personal brand by asking them a series of questions.",
    Agent.DEPLOY: "Assists with deploying your agent to the agentverse with an agent id.",
    Agent.GITHUB: "Assists with managing or connecting your GitHub profile.",
    Agent.DELETE: "Assists with deleting your data from your personal brand.",
}
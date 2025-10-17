from enum import Enum

class Agent(Enum):
    ONBOARDING = "onboarding_agent"
    FALLBACK = "fallback_agent"
    LINKEDIN = "linkedin_agent"
    GITHUB = "github_agent"
    RESUME = "resume_agent"

# Descriptions for each agent for the intent router to use
AGENT_DESCRIPTIONS = {
    Agent.ONBOARDING: "Handles onboarding new users and collecting initial information.",
    Agent.FALLBACK: "Handles unclear, ambiguous, or unsupported user intents.",
    Agent.LINKEDIN: "Assists with managing or connecting your LinkedIn profile.",
    Agent.GITHUB: "Assists with managing or connecting your GitHub profile.",
    Agent.RESUME: "Helps with uploading, reviewing, or managing your resume.",
}
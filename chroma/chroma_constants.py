from enum import Enum

COLLECTION = "user_facts"

class Source(Enum):
    UNKNOWN = "unknown"
    RESUME = "resume"
    GITHUB = "github"
    LINKEDIN = "linkedin"
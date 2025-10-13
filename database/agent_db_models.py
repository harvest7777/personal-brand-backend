from pydantic import BaseModel 
from typing import List, Literal

class JsonMesasge(BaseModel):
    role: Literal["human", "ai"]
    content: str

class JsonAgentState(BaseModel):
    current_step: int
    current_agent: str
    messages: List[JsonMesasge]
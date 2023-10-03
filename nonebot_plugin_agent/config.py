from typing import Dict, Optional, Any

from pydantic import BaseModel, Field
from .llm import LLM_Type


class AgentConfig(BaseModel):
    agent_llm_type: str = Field(default=LLM_Type.OPENAI)
    agent_llm_kwargs: Optional[Dict[str, Any]] = Field(default={})

    agent_max_calling_round_per_query: int = Field(default=10)
    agent_max_timeout_in_seconds_per_request: int = Field(default=10)

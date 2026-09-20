import pydantic

class SystemOutput(pydantic.BaseModel):

    article: str
    latency: float
    token_usage: int

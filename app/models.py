from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class ProgressEvent(BaseModel):
    type: Literal["challenge_result", "checkpoint_reached", "custom"]
    challenge_id: Optional[str] = None
    correct: Optional[bool] = None
    time_ms: Optional[int] = None
    score_delta: Optional[int] = 0
    level: Optional[int] = None
    node: Optional[str] = None
    ts: Optional[str] = None  # ISO string from client (optional)

class SubmitProgressRequest(BaseModel):
    player_id: str
    game_id: str
    session_id: Optional[str] = None
    events: List[ProgressEvent]

class Stats(BaseModel):
    player_id: str
    game_id: str
    totals: dict = Field(default_factory=dict)  # plays, attempts, correct, time_ms, score
    accuracy: float = 0.0
    last_played: Optional[str] = None

class StatsResponse(BaseModel):
    global_stats: dict
    per_game: dict  # {game_id: {...}}

class LeaderboardEntry(BaseModel):
    rank: int
    player_id: str
    display_name: Optional[str] = None
    score: int

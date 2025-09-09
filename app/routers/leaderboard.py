from fastapi import APIRouter, Query
from ..services import get_leaderboard

router = APIRouter()

@router.get("/leaderboard/{game_id}")
def leaderboard(game_id: str,
               metric: str = Query("score"),
               page: int = 1,
               page_size: int = 50):
    entries = get_leaderboard(game_id, metric, page, page_size)
    return {"game_id": game_id, "metric": metric, "page": page, "page_size": page_size, "entries": entries}

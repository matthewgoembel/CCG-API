from fastapi import APIRouter
from ..services import get_stats

router = APIRouter()

@router.get("/stats/{player_id}")
def stats_global(player_id: str):
    return get_stats(player_id)

@router.get("/stats/{player_id}/{game_id}")
def stats_game(player_id: str, game_id: str):
    data = get_stats(player_id)
    return {"player_id": player_id, "game_id": game_id, **data["per_game"].get(game_id, {})}

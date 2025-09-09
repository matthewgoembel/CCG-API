from fastapi import APIRouter
from ..services import get_achievements

router = APIRouter()

@router.get("/achievements/{player_id}")
def achievements(player_id: str):
    return {"player_id": player_id, "achievements": get_achievements(player_id)}

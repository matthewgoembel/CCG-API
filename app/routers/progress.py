from fastapi import APIRouter, Header
from ..models import SubmitProgressRequest
from ..services import submit_progress

router = APIRouter()

@router.post("/progress/submit")
def submit(req: SubmitProgressRequest, x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key")):
    result, new_ach = submit_progress(req, x_idempotency_key)
    return {"ok": True, "new_achievements": new_ach, **result}

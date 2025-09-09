from datetime import datetime, timezone
from typing import List, Tuple
from pymongo.collection import Collection
from .db import get_db
from .models import SubmitProgressRequest, ProgressEvent

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def submit_progress(req: SubmitProgressRequest, idem_key: str | None = None) -> Tuple[dict, list[str]]:
    db = get_db()
    events_col: Collection = db["events"]
    stats_col: Collection = db["stats"]
    ach_col: Collection = db["player_achievements"]

    # idempotency (optional light)
    if idem_key:
        exists = events_col.find_one({"idempotent_key": idem_key}, {"_id": 1})
        if exists:
            # Return current stats for convenience
            st = stats_col.find_one({"player_id": req.player_id, "game_id": req.game_id}) or {}
            return {"updated_stats": st}, []

    # 1) insert events
    docs = []
    attempts = correct = score = time_ms = plays = 0
    for ev in req.events:
        ts = ev.ts or _now_iso()
        if ev.type == "challenge_result":
            attempts += 1
            if ev.correct:
                correct += 1
            score += int(ev.score_delta or 0)
            time_ms += int(ev.time_ms or 0)
            plays += 1  # count a 'play' per challenge result

        docs.append({
            "player_id": req.player_id,
            "game_id": req.game_id,
            "session_id": req.session_id,
            "type": ev.type,
            "payload": ev.dict(),
            "ts": ts,
            "idempotent_key": idem_key,
            "created_at": _now_iso(),
        })
    if docs:
        events_col.insert_many(docs)

    # 2) upsert stats
    inc = {
        "totals.plays": plays,
        "totals.attempts": attempts,
        "totals.correct": correct,
        "totals.time_ms": time_ms,
        "totals.score": score,
    }
    stats_col.update_one(
        {"player_id": req.player_id, "game_id": req.game_id},
        {"$inc": inc, "$set": {"last_played": _now_iso()}},
        upsert=True,
    )
    stat = stats_col.find_one({"player_id": req.player_id, "game_id": req.game_id}, {"_id": 0}) or {}

    # derive accuracy for response (optional to persist)
    t = stat.get("totals", {})
    attempts_tot = int(t.get("attempts", 0))
    correct_tot = int(t.get("correct", 0))
    acc = (correct_tot / attempts_tot) if attempts_tot else 0.0
    stat["accuracy"] = round(acc, 4)

    # 3) simple achievements (example thresholds)
    new_ach = []
    thresholds = [10, 50, 100]
    for th in thresholds:
        aid = f"ach_correct_{th}"
        already = ach_col.find_one({"player_id": req.player_id, "achievement_id": aid})
        if not already and correct_tot >= th:
            ach_col.insert_one({
                "player_id": req.player_id,
                "achievement_id": aid,
                "earned_at": _now_iso(),
            })
            new_ach.append(aid)

    return {"updated_stats": stat}, new_ach

def get_stats(player_id: str):
    db = get_db()
    cur = db["stats"].find({"player_id": player_id}, {"_id": 0})
    per_game = {doc["game_id"]: doc for doc in cur}
    # compute global aggregates
    global_tot = {"plays":0,"attempts":0,"correct":0,"time_ms":0,"score":0}
    for g in per_game.values():
        t = g.get("totals", {})
        for k in global_tot:
            global_tot[k] += int(t.get(k, 0))
    acc = (global_tot["correct"] / global_tot["attempts"]) if global_tot["attempts"] else 0.0
    return {"global_stats": {**global_tot, "accuracy": round(acc,4)}, "per_game": per_game}

def get_achievements(player_id: str):
    db = get_db()
    cur = db["player_achievements"].find({"player_id": player_id}, {"_id": 0})
    return list(cur)

def get_leaderboard(game_id: str, metric: str, page: int, page_size: int):
    db = get_db()
    page = max(page, 1); page_size = min(max(page_size, 1), 100)
    skip = (page - 1) * page_size
    sort_field = f"totals.{metric}" if metric in ("score","time_ms","plays","attempts","correct") else "totals.score"

    cur = db["stats"].find({"game_id": game_id}).sort(sort_field, -1).skip(skip).limit(page_size)
    entries = []
    rank_start = skip + 1
    for i, doc in enumerate(cur):
        totals = doc.get("totals", {})
        entries.append({
            "rank": rank_start + i,
            "player_id": doc["player_id"],
            "score": int(totals.get("score", 0)),
        })
    return entries

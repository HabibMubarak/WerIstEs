import json
import os
from appwrite.client import Client
from appwrite.services.databases import Databases


def _parse_request_body(req):
    raw = getattr(req, 'body', None)
    if isinstance(raw, dict):
        return raw
    if raw is None:
        return {}
    if isinstance(raw, (bytes, bytearray)):
        try:
            raw = raw.decode('utf-8')
        except Exception:
            return {}
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except Exception:
            return {}
    try:
        return json.loads(str(raw))
    except Exception:
        return {}


def main(context):
    payload = _parse_request_body(context.req)
    if not payload:
        return context.res.json({"error": "Invalid or empty JSON body"}, 400)

    room_id = payload.get("roomId")
    user_id = payload.get("userId")
    question = payload.get("question")
    answer = payload.get("answer")

    if not room_id or not user_id:
        return context.res.json({"error": "roomId and userId required"}, 400)

    # --- Appwrite setup ---
    client = (
        Client()
        .set_endpoint(os.environ["APPWRITE_FUNCTION_API_ENDPOINT"])
        .set_project(os.environ["APPWRITE_FUNCTION_PROJECT_ID"])
        .set_key(os.environ["APPWRITE_API_KEY"])
    )
    db = Databases(client)

    DATABASE_ID = os.environ["MY_DB_ID"]
    COLLECTION_ID = os.environ["MY_COLLECTION_ID"]

    # --- Raum holen ---
    try:
        room = db.get_document(DATABASE_ID, COLLECTION_ID, room_id)
    except Exception as e:
        return context.res.json({"error": f"Room not found: {e}"}, 404)

    players = room.get("players", [])
    current_turn = room.get("current_turn")
    room_state = room.get("state")

    # --- Prüfen, ob Raum bereit ist ---
    if len(players) < 2:
        return context.res.json({"error": "Room does not have 2 players yet."}, 400)

    # --- Frage stellen ---
    if question:
        next_turn = players[1] if user_id == players[0] else players[0]
        update_data = {
            "question": question,
            "answer": "",
            "current_turn": next_turn,
            "state": "playing"
        }
        db.update_document(DATABASE_ID, COLLECTION_ID, room_id, data=update_data)
        return context.res.json({
            "status": "ok",
            "type": "question",
            "message": "Frage gespeichert",
            "current_turn": next_turn,
            "question": question
        })

    # --- Antwort geben ---
    elif answer:
        next_turn = user_id
        update_data = {
            "answer": answer,
            "current_turn": next_turn,
            "state": "playing",
            "question": ""
        }
        db.update_document(DATABASE_ID, COLLECTION_ID, room_id, data=update_data)
        return context.res.json({
            "status": "ok",
            "type": "answer",
            "message": "Antwort gespeichert",
            "answer": answer,
            "current_turn": next_turn
        })

    # --- Kein Frage/Aantwort-Request ---
    else:
        # Einfach aktuellen Zustand zurückgeben
        return context.res.json({
            "roomId": room_id,
            "players": players,
            "current_turn": current_turn,
            "question": room.get("question", ""),
            "answer": room.get("answer", ""),
            "state": room_state
        })

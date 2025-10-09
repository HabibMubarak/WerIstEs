import json
import os
from appwrite.client import Client
from appwrite.services.databases import Databases


def _parse_request_body(req):
    try:
        # Appwrite liefert body meist als String
        raw = getattr(req, "body", None)
        if not raw:
            return {}

        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")

        if isinstance(raw, dict):
            return raw

        raw = raw.strip()

        # Versuch 1: echtes JSON
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Versuch 2: Fallback – eval()-ähnliche Struktur, z. B. mit '
        fixed = raw.replace("'", '"')
        return json.loads(fixed)

    except Exception as e:
        return {"_parse_error": str(e)}



def main(context):
    payload = _parse_request_body(context.req)
    context.log(f"Incoming payload raw: {getattr(context.req, 'body', None)}")
    context.log(f"Parsed payload: {_parse_request_body(context.req)}")
    if not payload:
        return context.res.json({"error": "Invalid or empty JSON body"}, 400)
    
    room_id = payload.get("roomId")
    user_id = payload.get("userId")
    question = payload.get("question")
    answer = payload.get("answer")
    finish_state = payload.get("state")
    winner = payload.get("winner")


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
        players = room.get("players", [])
        current_turn = room.get("current_turn")
        room_state = room.get("state")
    except Exception as e:
        return context.res.json({"error": f"Room not found: {e}"}, 404)

    

    # --- Prüfen, ob Raum bereit ist ---
    if len(players) < 2:
        return context.res.json({"error": "Room does not have 2 players yet."}, 400)
    
    # --- Spiel beenden ---
    if finish_state == "finish" and winner:
        # Hole aktuelles winner_ack, Standard: leere Liste
        winner_ack = room.get("winner_ack", [])

        if user_id not in winner_ack:
            winner_ack.append(user_id)

        update_data = {
            "state": "finish",
            "winner": winner,
            "winner_ack": winner_ack
        }
        context.log(f"Finish request: {update_data}")

        # Prüfen, ob beide Spieler auf WinnerScreen sind
        if set(winner_ack) >= set(players):
            # Raum löschen
            try:
                db.delete_document(DATABASE_ID, COLLECTION_ID, room_id)
                return context.res.json({
                    "status": "ok",
                    "message": f"Spiel beendet, Gewinner: {winner}, Raum gelöscht",
                    "state": "finish",
                    "winner": winner,
                    "room_deleted": True
                })
            except Exception as e:
                return context.res.json({
                    "status": "error",
                    "message": f"Fehler beim Löschen des Raums: {str(e)}"
                }, 500)
        else:
            # Aktualisieren, wenn noch nicht beide Spieler da sind
            db.update_document(DATABASE_ID, COLLECTION_ID, room_id, data=update_data)
            return context.res.json({
                "status": "ok",
                "message": f"Spiel beendet, Gewinner: {winner}",
                "state": "finish",
                "winner": winner,
                "winner_ack": winner_ack
            })


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
        try:
            update_data = {
                "answer": answer,
                "current_turn": user_id,
                "state": "answer_sent"
            }
            db.update_document(DATABASE_ID, COLLECTION_ID, room_id, data=update_data)
            return context.res.json({
                "status": "ok",
                "type": "answer",
                "message": "Antwort gespeichert",
                "answer": answer,
                "current_turn": user_id,
                "state": "answer_sent"
            })
        except Exception as e:
            context.error(f"Beim Speichern der Antwort ist ein Fehler aufgetreten: {repr(e)}")
            return context.res.json({
            "error": f"Beim Speichern der Antwort ist ein Fehler aufgetreten: {str(e)}",
            "trace": repr(e)
        }, 500)

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
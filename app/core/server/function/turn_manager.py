import json
import os
from appwrite.client import Client
from appwrite.services.databases import Databases


def _parse_request_body(req):
    """
    Parses the request body from the Appwrite context.
    Handles raw bytes, strings, and dictionary inputs.
    """
    raw = getattr(req, "body", None)
    
    if not raw:
        return {}

    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    
    if isinstance(raw, dict):
        return raw

    if not isinstance(raw, str):
        return {}

    raw = raw.strip()

    # Attempt 1: Standard JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Attempt 2: Fallback for dictionary-like string (e.g., uses single quotes)
    try:
        # Dangerous eval-like replacement: replace single quotes with double quotes. 
        # Only do this if standard JSON parsing failed.
        fixed = raw.replace("'", '"')
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass
    except Exception as e:
        # Catch unexpected errors during fallback parsing
        return {"_parse_error": str(e)}

    return {}


def main(context):
    payload = _parse_request_body(context.req)
    # Logging the raw body can help diagnose non-JSON 500 errors
    context.log(f"Incoming body: {getattr(context.req, 'body', None)}") 
    context.log(f"Parsed payload: {payload}")
    
    if not payload:
        return context.res.json({"error": "Invalid or empty JSON body"}, 400)
    
    # Check for parsing error from the internal function
    if "_parse_error" in payload:
        context.error(f"Failed to parse body: {payload['_parse_error']}")
        return context.res.json({"error": "Failed to parse request body."}, 400)

    room_id = payload.get("roomId")
    user_id = payload.get("userId")
    question = payload.get("question")
    answer = payload.get("answer")
    finish_state = payload.get("state")
    winner = payload.get("winner")


    if not room_id or not user_id:
        return context.res.json({"error": "roomId and userId required"}, 400)

    # --- Appwrite setup ---
    try:
        client = (
            Client()
            .set_endpoint(os.environ["APPWRITE_FUNCTION_API_ENDPOINT"])
            .set_project(os.environ["APPWRITE_FUNCTION_PROJECT_ID"])
            .set_key(os.environ["APPWRITE_API_KEY"])
        )
        db = Databases(client)

        DATABASE_ID = os.environ["MY_DB_ID"]
        COLLECTION_ID = os.environ["MY_COLLECTION_ID"]
    except KeyError as e:
        context.error(f"Missing environment variable: {e}")
        return context.res.json({"error": f"Missing required environment variable: {e}"}, 500)


    # --- Raum holen ---
    try:
        room = db.get_document(DATABASE_ID, COLLECTION_ID, room_id)
        players = room.get("players", [])
        current_turn = room.get("current_turn")
        room_state = room.get("state")
        
        if user_id not in players:
            return context.res.json({"error": "User is not a member of this room."}, 403)
            
    except Exception as e:
        context.error(f"DB Read Error (get_document): {e}")
        return context.res.json({"error": f"Room not found or database read error: {e}"}, 404)

    

    # --- Prüfen, ob Raum bereit ist ---
    if len(players) < 2:
        return context.res.json({"error": "Room does not have 2 players yet."}, 400)
    
    # --- Spiel beenden ---
    if finish_state == "finish" and winner:
        winner_ack = room.get("winner_ack", [])
        if user_id not in winner_ack:
            winner_ack.append(user_id)

        # Erst speichern
        update_data = {
            "state": "finish",
            "winner": winner,
            "winner_ack": winner_ack
        }
        try:
            # IMPORTANT: Added explicit logging before critical DB operations
            context.log(f"Attempting to update room {room_id} with finish state.")
            db.update_document(DATABASE_ID, COLLECTION_ID, room_id, data=update_data)
            context.log(f"Updated room {room_id} with winner={winner} and winner_ack={winner_ack}")
        except Exception as e:
            # This is the path most likely to lead to a 500. Error log improved.
            context.error(f"DB update failed during finish state: {repr(e)}")
            return context.res.json({
                "status": "error",
                "message": f"DB Update failed: {str(e)}"
            }, 500)

        # Dann prüfen, ob beide Spieler da sind
        if set(winner_ack) >= set(players):
            try:
                context.log(f"Both players acknowledged winner. Deleting room {room_id}.")
                db.delete_document(DATABASE_ID, COLLECTION_ID, room_id)
                return context.res.json({
                    "status": "ok",
                    "message": f"Spiel beendet, Gewinner: {winner}, Raum gelöscht",
                    "state": "finish",
                    "winner": winner,
                    "room_deleted": True
                })
            except Exception as e:
                context.error(f"DB delete failed: {repr(e)}")
                return context.res.json({
                    "status": "error",
                    "message": f"Fehler beim Löschen des Raums: {str(e)}"
                }, 500)

        # Wenn noch nicht alle Spieler da sind
        return context.res.json({
            "status": "ok",
            "message": f"Spiel beendet, Gewinner: {winner}",
            "state": "finish",
            "winner": winner,
            "winner_ack": winner_ack,
            "character_data": room.get("character_data", {}) # Pass character data back for the winner screen
        })


    # --- Frage stellen ---
    if question:
        # Check if it's the user's turn to ask (Only applicable if state handling logic is external/omitted here)
        # Assuming the client handles the turn check and only sends the request if it's their turn.
        # The Appwrite function should enforce this by checking `current_turn`.
        if current_turn != user_id and room_state != "answer_sent":
             context.log(f"User {user_id} tried to ask a question, but it's not their turn ({current_turn}).")
             return context.res.json({"error": "Du bist nicht am Zug!"}, 403)
             
        next_turn = players[1] if user_id == players[0] else players[0]
        update_data = {
            "question": question,
            "answer": "",
            "current_turn": next_turn,
            "state": "playing" # Next player is now "playing" (answering phase)
        }
        try:
            db.update_document(DATABASE_ID, COLLECTION_ID, room_id, data=update_data)
        except Exception as e:
            context.error(f"DB update failed during question send: {repr(e)}")
            return context.res.json({"error": f"DB Update failed on question: {str(e)}"}, 500)
            
        return context.res.json({
            "status": "ok",
            "type": "question",
            "message": "Frage gespeichert",
            "current_turn": next_turn,
            "question": question
        })

    # --- Antwort geben ---
    elif answer:
        # The person who just asked the question is waiting for an answer.
        # It should be the *other* player's turn to answer (the one who receives the question).
        if current_turn != user_id and room_state != "playing":
            context.log(f"User {user_id} tried to answer, but it's not the answer phase (current turn: {current_turn}, state: {room_state}).")
            return context.res.json({"error": "Du bist nicht dran mit Antworten!"}, 403)

        try:
            update_data = {
                "answer": answer,
                # Turn goes back to the questioner to process the answer
                "current_turn": players[1] if user_id == players[0] else players[0],
                "state": "answer_sent"
            }
            db.update_document(DATABASE_ID, COLLECTION_ID, room_id, data=update_data)
            return context.res.json({
                "status": "ok",
                "type": "answer",
                "message": "Antwort gespeichert",
                "answer": answer,
                "current_turn": update_data["current_turn"],
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
            "state": room_state,
            "winner": room.get("winner", None),
            # Send character data on poll for winner screen preparation
            "character_data": room.get("character_data", {}) 
        })
